import json
from typing import Annotated
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.import_ import DetectTabsResponse, ImportSummary
from database import get_db
from models.staff import Staff
from models.document import Document, document_assignees
from models.directive import Directive, directive_assignees
from models.import_log import ImportLog
from services.excel_parser import ExcelParser
from auth import CurrentUser
import io
from uuid import uuid4

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/detect-tabs", response_model=DetectTabsResponse)
async def detect_tabs(
    current_user: CurrentUser,
    file: Annotated[UploadFile, File(...)],
):
    contents = await file.read()
    parser = ExcelParser(io.BytesIO(contents))
    result = parser.detect_tabs()
    return DetectTabsResponse(
        sheet_names=result["sheet_names"],
        suggested=result["suggested"]
    )


@router.post("/tab-preview")
async def tab_preview(
    tab_name: str,
    header_row: int,
    current_user: CurrentUser,
    file: Annotated[UploadFile, File(...)],
):
    contents = await file.read()
    parser = ExcelParser(io.BytesIO(contents))
    return parser.get_tab_preview(tab_name, header_row)


@router.post("/preview")
async def preview_import(
    config: Annotated[str, Form(...)],
    current_user: CurrentUser,
    file: Annotated[UploadFile, File(...)],
):
    tab_configs = json.loads(config)
    contents = await file.read()
    parser = ExcelParser(io.BytesIO(contents))
    result = parser.parse(tab_configs)
    return {
        "summary": result["summary"],
        "flagged": result["flagged"],
        "staff": result["staff"]
    }


@router.post("/confirm", response_model=ImportSummary)
async def confirm_import(
    config: Annotated[str, Form(...)],
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
):
    tab_configs = json.loads(config)
    contents = await file.read()
    parser = ExcelParser(io.BytesIO(contents))
    result = parser.parse(tab_configs)

    # 1. upsert staff
    staff_map = {}
    for name in result["staff"]:
        existing_result = await db.execute(select(Staff).where(Staff.short_name == name))
        existing = existing_result.scalars().first()
        if existing:
            staff_map[name] = existing.id
        else:
            new_staff = Staff(id=uuid4(), short_name=name, full_name=name, is_active=True)
            db.add(new_staff)
            await db.flush()
            staff_map[name] = new_staff.id

    # 2. insert documents
    docs_imported = 0
    rows_skipped = 0
    for doc in result["documents"]:
        existing = await db.execute(
            select(Document).where(
                Document.content_summary == doc["content"],
                Document.status != "cancelled"
            )
        )
        if existing.scalars().first():
            rows_skipped += 1
            continue

        new_doc = Document(
            id=uuid4(),
            content_summary=doc["content"],
            deadline=doc["deadline"],
            is_recurring=doc["is_recurring"],
            recurrence_label=doc["recurrence_label"],
            status=doc["status"],
            imported_by=current_user.id,
        )
        db.add(new_doc)
        await db.flush()

        for name in doc["staff_names"]:
            if name in staff_map:
                await db.execute(document_assignees.insert().values(
                    id=uuid4(), document_id=new_doc.id, staff_id=staff_map[name]
                ))
        docs_imported += 1

    # 3. insert directives
    dirs_imported = 0
    for directive in result["directives"]:
        existing = await db.execute(
            select(Directive).where(
                Directive.directive_content == directive["content"],
                Directive.status != "cancelled"
            )
        )
        if existing.scalars().first():
            rows_skipped += 1
            continue

        new_dir = Directive(
            id=uuid4(),
            directive_content=directive["content"],
            deadline=directive["deadline"],
            is_recurring=directive["is_recurring"],
            recurrence_label=directive["recurrence_label"],
            status=directive["status"],
            imported_by=current_user.id,
        )
        db.add(new_dir)
        await db.flush()

        for name in directive["staff_names"]:
            if name in staff_map:
                await db.execute(directive_assignees.insert().values(
                    id=uuid4(), directive_id=new_dir.id, staff_id=staff_map[name]
                ))
        dirs_imported += 1

    # 4. save import log
    db.add(ImportLog(
        id=uuid4(),
        source_tab=" | ".join(c["tab_name"] for c in tab_configs),
        filename=file.filename,
        rows_imported=docs_imported + dirs_imported,
        rows_skipped=rows_skipped,
        rows_flagged=len(result["flagged"]),
        imported_by=current_user.id,
    ))

    await db.commit()

    return ImportSummary(
        documents_parsed=docs_imported,
        directives_parsed=dirs_imported,
        total_flagged=len(result["flagged"]),
        staff_found=len(result["staff"])
    )
