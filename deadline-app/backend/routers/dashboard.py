from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.staff import Staff
from models.document import Document, document_assignees
from models.directive import Directive, directive_assignees
from schemas.dashboard import DashboardResponse, TaskSummary, StaffSummary
from routers.deps import get_current_user
from datetime import date
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

URGENT_DAYS = 1
RED_DAYS = 3
YELLOW_DAYS = 7

def get_urgency(deadline: Optional[date], is_recurring: bool) -> str:
    if is_recurring or not deadline:
        return "green"
    
    days = (deadline - date.today()).days

    if days < 0:
        return "overdue"
    elif days <= URGENT_DAYS:
        return "red_urgent"
    elif days <= RED_DAYS:
        return "red"
    elif days <= YELLOW_DAYS:
        return "yellow"
    else:
        return "green"
    
def get_days_remaining(deadline: Optional[date], is_recurring: bool):
    if is_recurring or not deadline:
        return None
    return (deadline - date.today()).days

def get_staff_names_for_doc(doc_id: UUID, db: Session) -> list[str]:
    result = db.execute(
        document_assignees.select().where(
            document_assignees.c.document_id == doc_id
        )
    ).fetchall()

    staff_names = []
    for row in result:
        staff = db.query(Staff).filter(Staff.id == row.staff_id).first()
        if staff:
            staff_names.append(staff.short_name)
    return staff_names

def get_staff_names_for_directive(dir_id: UUID, db: Session) -> list[str]:
    result = db.execute(
        directive_assignees.select().where(
            directive_assignees.c.directive_id == dir_id
        )
    ).fetchall()

    staff_names = []
    for row in result:
        staff = db.query(Staff).filter(Staff.id == row.staff_id).first()
        if staff:
            staff_names.append(staff.short_name)
    return staff_names

def get_doc_ids_for_staff(staff_id: UUID, db: Session) -> list:
    rows = db.execute(
        document_assignees.select().where(
            document_assignees.c.staff_id == staff_id
        )
    ).fetchall()
    return [row.document_id for row in rows]

def get_dir_ids_for_staff(staff_id: UUID, db: Session) -> list:
    rows = db.execute(
        directive_assignees.select().where(
            directive_assignees.c.staff_id == staff_id
        )
    ).fetchall()
    return [row.directive_id for row in rows]

@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    #get all active tasks - not done or cancelled
    active_statuses = ["pending", "in_progress", "overdue"]

    documents = db.query(Document).filter(
        Document.status.in_(active_statuses),
        Document.content_summary.isnot(None),
        Document.content_summary != ""
    ).all()

    directives = db.query(Directive).filter(
        Directive.status.in_(active_statuses),
        Directive.directive_content.isnot(None),
        Directive.directive_content != ""
    ).all()

    #build task summaries
    all_tasks = []

    for doc in documents:
        urgency = get_urgency(doc.deadline, doc.is_recurring)
        all_tasks.append(TaskSummary(
            id=doc.id,
            content=doc.content_summary or "",
            deadline=doc.deadline,
            days_remaining=get_days_remaining(doc.deadline, doc.is_recurring),
            urgency=urgency,
            status=doc.status,
            is_recurring=doc.is_recurring,
            source="document",
            staff_names=get_staff_names_for_doc(doc.id, db)
        ))

    for directive in directives:
        urgency = get_urgency(directive.deadline, directive.is_recurring)
        all_tasks.append(TaskSummary(
            id=directive.id,
            content=directive.directive_content or "",
            deadline=directive.deadline,
            days_remaining=get_days_remaining(directive.deadline, directive.is_recurring),
            urgency=urgency,
            status=directive.status,
            is_recurring=directive.is_recurring,
            source="directive",
            staff_names=get_staff_names_for_directive(directive.id, db)
        ))

    # group by urgency
    grouped = {
        "overdue": [],
        "red_urgent": [],
        "red": [],
        "yellow": [],
        "green": []
    }

    for task in all_tasks:
        grouped[task.urgency].append(task)

    return DashboardResponse(
        overdue=grouped["overdue"],
        red_urgent=grouped["red_urgent"],
        red=grouped["red"],
        yellow=grouped["yellow"],
        green=grouped["green"],
        summary={
            "total_overdue": len(grouped["overdue"]),
            "total_red_urgent": len(grouped["red_urgent"]),
            "total_red": len(grouped["red"]),
            "total_yellow": len(grouped["yellow"]),
            "total_green": len(grouped["green"]),
            "total_active": len(all_tasks)
        }
    )

@router.get("/staff", response_model=list[StaffSummary])
async def get_staff(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    staff_list = db.query(Staff).filter(Staff.is_active).all()
    result = []

    for staff in staff_list:
        #count pending tasks from documents
        doc_ids = get_doc_ids_for_staff(staff.id, db)

        # directives
        dir_ids = get_dir_ids_for_staff(staff.id, db)

        doc_pending = db.query(Document).filter(
            Document.id.in_(doc_ids),
            Document.status.in_(["pending", "in_progress"])
        ).count() if doc_ids else 0

        dir_pending = db.query(Directive).filter(
            Directive.id.in_(dir_ids),
            Directive.status.in_(["pending", "in_progress"])
        ).count() if dir_ids else 0

        pending_count = doc_pending + dir_pending

        doc_overdue = db.query(Document).filter(
            Document.id.in_(doc_ids),
            Document.status == "overdue"
        ).count() if doc_ids else 0

        dir_overdue = db.query(Directive).filter(
            Directive.id.in_(dir_ids),
            Directive.status == "overdue"
        ).count() if dir_ids else 0

        overdue_count = doc_overdue + dir_overdue

        result.append(StaffSummary(
            id=staff.id,
            short_name=staff.short_name,
            full_name=staff.full_name,
            pending_count=pending_count,
            overdue_count=overdue_count
        ))
    
    return result

@router.get("/staff/{staff_id}", response_model=list[TaskSummary])
async def get_staff_tasks(
    staff_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc_ids = get_doc_ids_for_staff(staff_id, db)
    dir_ids = get_dir_ids_for_staff(staff_id, db)

    tasks = []

    for doc_id in doc_ids:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            tasks.append(TaskSummary(
                id=doc.id,
                content=doc.content_summary or "",
                deadline=doc.deadline,
                days_remaining=get_days_remaining(doc.deadline, doc.is_recurring),
                urgency=get_urgency(doc.deadline, doc.is_recurring),
                status=doc.status,
                is_recurring=doc.is_recurring,
                source="document",
                staff_names=get_staff_names_for_doc(doc.id, db)
            ))

    for dir_id in dir_ids:
        directive = db.query(Directive).filter(Directive.id == dir_id).first()
        if directive:
            tasks.append(TaskSummary(
                id=directive.id,
                content=directive.directive_content or "",
                deadline=directive.deadline,
                days_remaining=get_days_remaining(directive.deadline, directive.is_recurring),
                urgency=get_urgency(directive.deadline, directive.is_recurring),
                status=directive.status,
                is_recurring=directive.is_recurring,
                source="directive",
                staff_names=get_staff_names_for_directive(directive.id, db)
            ))

    return sorted(tasks, key=lambda t: (
        t.days_remaining is None,
        t.days_remaining if t.days_remaining is not None else 999
    ))

