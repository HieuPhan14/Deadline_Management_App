from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from schemas.import_ import DetectTabsResponse, ImportSummary
from routers.deps import get_current_user
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.staff import Staff
from models.document import Document, document_assignees
from models.directive import Directive, directive_assignees
from models.import_log import ImportLog
from services.excel_parser import ExcelParser
import io
from uuid import uuid4


router = APIRouter(prefix="/import", tags=["import"])

@router.post("/detect-tabs", response_model=DetectTabsResponse)
async def detect_tabs(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    parser = ExcelParser(io.BytesIO(contents))
    result = parser.detect_tabs()
    return DetectTabsResponse(
        sheet_names=result["sheet_names"],
        suggested=result["suggested"]
    )

@router.post("/preview")
async def preview_import(
    tab1_name: str,
    tab2_name: str,
    file: UploadFile=File(...),
    current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    parser = ExcelParser(io.BytesIO(contents))
    result = parser.parse(tab1_name, tab2_name)
    return {
        "summary": result["summary"],
        "flagged": result["flagged"],
        "staff": result["staff"]
    }

@router.post("/confirm", response_model=ImportSummary)
async def confirm_import(
    tab1_name: str,
    tab2_name: str,
    file: UploadFile=File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contents = await file.read()
    parser = ExcelParser(io.BytesIO(contents))
    result = parser.parse(tab1_name, tab2_name)

    #1. upsert staff
    staff_map = {}
    for name in result["staff"]:
        existing = db.query(Staff).filter(Staff.short_name == name).first()
        if existing:
            staff_map[name] = existing.id 
        else:
            new_staff = Staff(
                id=uuid4(),
                short_name=name,
                full_name=name,
                is_active=True
            )
            db.add(new_staff)
            db.flush()
            staff_map[name] = new_staff.id

    #2. insert documents
    docs_imported = 0
    for doc in result["documents"]:
        new_doc = Document(
            id=uuid4(),
            row_number=doc["row_number"],
            received_date=doc["received_date"],
            document_type=doc["document_type"],
            content_summary=doc["content_summary"],
            reference_number=doc["reference_number"],
            requirement=doc["requirement"],
            deadline=doc["deadline"],
            is_recurring=doc["is_recurring"],
            recurrence_label=doc["recurrence_label"],
            status=doc["status"],
            result=doc["result"],
            notes=doc["notes"],
            imported_by=current_user.id
        )

        db.add(new_doc)
        db.flush()

        # insert assignees
        for name in doc["staff_names"]:
            if name in staff_map:
                db.execute(
                    document_assignees.insert().values(
                        id=uuid4(),
                        document_id=new_doc.id,
                        staff_id=staff_map[name]
                    )
                )
        docs_imported += 1

    #3. insert directives
    dirs_imported = 0
    for directive in result["directives"]:
        new_dir = Directive(
            id=uuid4(),
            row_number=directive["row_number"],
            meeting_date=directive["meeting_date"],
            directive_content=directive["directive_content"],
            deadline=directive["deadline"],
            is_recurring=directive["is_recurring"],
            recurrence_label=directive["recurrence_label"],
            status=directive["status"],
            result=directive["result"],
            notes=directive["notes"],
            imported_by=current_user.id
        )

        db.add(new_dir)
        db.flush()

        # insert assignees
        for name in directive["staff_names"]:
            if name in staff_map:
                db.execute(
                    directive_assignees.insert().values(
                        id=uuid4(),
                        directive_id=new_dir.id,
                        staff_id=staff_map[name]
                    )
                )
        dirs_imported += 1

    # 4. save import log
    import_log = ImportLog(
        id=uuid4(),
        source_tab=f"{tab1_name} | {tab2_name}",
        filename=file.filename,
        rows_imported=docs_imported + dirs_imported,
        rows_skipped=0,
        rows_flagged=len(result["flagged"]),
        imported_by=current_user.id
    )
    db.add(import_log)

    # 5. commit everything
    db.commit()

    return ImportSummary(
        documents_parsed=docs_imported,
        directives_parsed=dirs_imported,
        total_flagged=len(result["flagged"]),
        staff_found=len(result["staff"])
    )
