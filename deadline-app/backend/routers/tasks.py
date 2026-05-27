from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.document import Document
from models.directive import Directive
from routers.deps import get_current_user
from uuid import UUID

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.patch("/documents/{doc_id}/cancel")
async def cancel_document(
    doc_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.status = "cancelled"
    db.commit()
    return {"message": "cancelled"}

@router.patch("/directives/{dir_id}/cancel")
async def cancel_directive(
    dir_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    directive = db.query(Directive).filter(Directive.id == dir_id).first()
    if not directive:
        raise HTTPException(status_code=404, detail="Directive not found")
    directive.status = "cancelled"
    db.commit()
    return {"message": "cancelled"}