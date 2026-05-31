from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.document import Document
from models.directive import Directive
from auth import CurrentUser
from uuid import UUID

router = APIRouter(prefix="/tasks", tags=["tasks"])


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
