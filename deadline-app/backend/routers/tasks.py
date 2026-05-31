from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models.document import Document, document_assignees
from models.directive import Directive, directive_assignees
from models.staff import Staff
from schemas.dashboard import TaskCreate, TaskUpdate
from auth import CurrentUser
from uuid import UUID, uuid4

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_or_create_staff(name: str, db: AsyncSession) -> Staff:
    result = await db.execute(select(Staff).where(Staff.short_name == name))
    staff = result.scalars().first()
    if not staff:
        staff = Staff(id=uuid4(), short_name=name, full_name=name, is_active=True)
        db.add(staff)
        await db.flush()
    return staff


@router.post("")
async def create_task(
    data: TaskCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if data.source == "directive":
        task = Directive(
            id=uuid4(),
            directive_content=data.content,
            deadline=data.deadline,
            status="pending",
            imported_by=current_user.id,
        )
        db.add(task)
        await db.flush()
        for name in data.staff_names:
            staff = await get_or_create_staff(name, db)
            await db.execute(directive_assignees.insert().values(
                id=uuid4(), directive_id=task.id, staff_id=staff.id
            ))
    else:
        task = Document(
            id=uuid4(),
            content_summary=data.content,
            deadline=data.deadline,
            status="pending",
            imported_by=current_user.id,
        )
        db.add(task)
        await db.flush()
        for name in data.staff_names:
            staff = await get_or_create_staff(name, db)
            await db.execute(document_assignees.insert().values(
                id=uuid4(), document_id=task.id, staff_id=staff.id
            ))

    await db.commit()
    return {"message": "created"}


@router.patch("/documents/{doc_id}")
async def update_document(
    doc_id: UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if data.content is not None:
        doc.content_summary = data.content
    if data.deadline is not None:
        doc.deadline = data.deadline
    if data.staff_names is not None:
        await db.execute(delete(document_assignees).where(document_assignees.c.document_id == doc_id))
        for name in data.staff_names:
            staff = await get_or_create_staff(name, db)
            await db.execute(document_assignees.insert().values(
                id=uuid4(), document_id=doc_id, staff_id=staff.id
            ))
    await db.commit()
    return {"message": "updated"}


@router.patch("/directives/{dir_id}")
async def update_directive(
    dir_id: UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Directive).where(Directive.id == dir_id))
    directive = result.scalars().first()
    if not directive:
        raise HTTPException(status_code=404, detail="Directive not found")
    if data.content is not None:
        directive.directive_content = data.content
    if data.deadline is not None:
        directive.deadline = data.deadline
    if data.staff_names is not None:
        await db.execute(delete(directive_assignees).where(directive_assignees.c.directive_id == dir_id))
        for name in data.staff_names:
            staff = await get_or_create_staff(name, db)
            await db.execute(directive_assignees.insert().values(
                id=uuid4(), directive_id=dir_id, staff_id=staff.id
            ))
    await db.commit()
    return {"message": "updated"}


@router.patch("/documents/{doc_id}/cancel")
async def cancel_document(
    doc_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.status = "cancelled"
    await db.commit()
    return {"message": "cancelled"}


@router.patch("/directives/{dir_id}/cancel")
async def cancel_directive(
    dir_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Directive).where(Directive.id == dir_id))
    directive = result.scalars().first()
    if not directive:
        raise HTTPException(status_code=404, detail="Directive not found")
    directive.status = "cancelled"
    await db.commit()
    return {"message": "cancelled"}
