from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models.staff import Staff
from models.document import Document, document_assignees
from models.directive import Directive, directive_assignees
from schemas.dashboard import DashboardResponse, TaskSummary, StaffSummary
from auth import CurrentUser
from datetime import date
from uuid import UUID
from services.scheduler import check_deadlines

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


async def get_staff_names_for_doc(doc_id: UUID, db: AsyncSession) -> list[str]:
    result = await db.execute(
        document_assignees.select().where(document_assignees.c.document_id == doc_id)
    )
    rows = result.fetchall()
    staff_names = []
    for row in rows:
        staff_result = await db.execute(select(Staff).where(Staff.id == row.staff_id))
        staff = staff_result.scalars().first()
        if staff:
            staff_names.append(staff.short_name)
    return staff_names


async def get_staff_names_for_directive(dir_id: UUID, db: AsyncSession) -> list[str]:
    result = await db.execute(
        directive_assignees.select().where(directive_assignees.c.directive_id == dir_id)
    )
    rows = result.fetchall()
    staff_names = []
    for row in rows:
        staff_result = await db.execute(select(Staff).where(Staff.id == row.staff_id))
        staff = staff_result.scalars().first()
        if staff:
            staff_names.append(staff.short_name)
    return staff_names


async def get_doc_ids_for_staff(staff_id: UUID, db: AsyncSession) -> list:
    result = await db.execute(
        document_assignees.select().where(document_assignees.c.staff_id == staff_id)
    )
    rows = result.fetchall()
    return [row.document_id for row in rows]


async def get_dir_ids_for_staff(staff_id: UUID, db: AsyncSession) -> list:
    result = await db.execute(
        directive_assignees.select().where(directive_assignees.c.staff_id == staff_id)
    )
    rows = result.fetchall()
    return [row.directive_id for row in rows]


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await check_deadlines()

    active_statuses = ["pending", "in_progress", "overdue"]

    doc_result = await db.execute(
        select(Document).where(
            Document.status.in_(active_statuses),
            Document.content_summary.isnot(None),
            Document.content_summary != ""
        )
    )
    documents = doc_result.scalars().all()

    dir_result = await db.execute(
        select(Directive).where(
            Directive.status.in_(active_statuses),
            Directive.directive_content.isnot(None),
            Directive.directive_content != ""
        )
    )
    directives = dir_result.scalars().all()

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
            staff_names=await get_staff_names_for_doc(doc.id, db)
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
            staff_names=await get_staff_names_for_directive(directive.id, db)
        ))

    grouped = {"overdue": [], "red_urgent": [], "red": [], "yellow": [], "green": []}
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
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    staff_result = await db.execute(select(Staff).where(Staff.is_active == True))
    staff_list = staff_result.scalars().all()
    result = []

    for staff in staff_list:
        doc_ids = await get_doc_ids_for_staff(staff.id, db)
        dir_ids = await get_dir_ids_for_staff(staff.id, db)

        if doc_ids:
            doc_pending_result = await db.execute(
                select(func.count(Document.id)).where(
                    Document.id.in_(doc_ids),
                    Document.status.in_(["pending", "in_progress"])
                )
            )
            doc_pending = doc_pending_result.scalar() or 0
        else:
            doc_pending = 0

        if dir_ids:
            dir_pending_result = await db.execute(
                select(func.count(Directive.id)).where(
                    Directive.id.in_(dir_ids),
                    Directive.status.in_(["pending", "in_progress"])
                )
            )
            dir_pending = dir_pending_result.scalar() or 0
        else:
            dir_pending = 0

        if doc_ids:
            doc_overdue_result = await db.execute(
                select(func.count(Document.id)).where(
                    Document.id.in_(doc_ids),
                    Document.status == "overdue"
                )
            )
            doc_overdue = doc_overdue_result.scalar() or 0
        else:
            doc_overdue = 0

        if dir_ids:
            dir_overdue_result = await db.execute(
                select(func.count(Directive.id)).where(
                    Directive.id.in_(dir_ids),
                    Directive.status == "overdue"
                )
            )
            dir_overdue = dir_overdue_result.scalar() or 0
        else:
            dir_overdue = 0

        result.append(StaffSummary(
            id=staff.id,
            short_name=staff.short_name,
            full_name=staff.full_name,
            pending_count=doc_pending + dir_pending,
            overdue_count=doc_overdue + dir_overdue
        ))

    return result


@router.get("/staff/{staff_id}", response_model=list[TaskSummary])
async def get_staff_tasks(
    staff_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    active = ["pending", "in_progress", "overdue"]

    doc_result = await db.execute(
        select(Document)
        .join(document_assignees, Document.id == document_assignees.c.document_id)
        .where(
            document_assignees.c.staff_id == staff_id,
            Document.status.in_(active),
            Document.content_summary.isnot(None),
            Document.content_summary != ""
        )
    )
    documents = doc_result.scalars().all()

    dir_result = await db.execute(
        select(Directive)
        .join(directive_assignees, Directive.id == directive_assignees.c.directive_id)
        .where(
            directive_assignees.c.staff_id == staff_id,
            Directive.status.in_(active),
            Directive.directive_content.isnot(None),
            Directive.directive_content != ""
        )
    )
    directives = dir_result.scalars().all()

    tasks = []

    for doc in documents:
        tasks.append(TaskSummary(
            id=doc.id,
            content=doc.content_summary or "",
            deadline=doc.deadline,
            days_remaining=get_days_remaining(doc.deadline, doc.is_recurring),
            urgency=get_urgency(doc.deadline, doc.is_recurring),
            status=doc.status,
            is_recurring=doc.is_recurring,
            source="document",
            staff_names=await get_staff_names_for_doc(doc.id, db)
        ))

    for directive in directives:
        tasks.append(TaskSummary(
            id=directive.id,
            content=directive.directive_content or "",
            deadline=directive.deadline,
            days_remaining=get_days_remaining(directive.deadline, directive.is_recurring),
            urgency=get_urgency(directive.deadline, directive.is_recurring),
            status=directive.status,
            is_recurring=directive.is_recurring,
            source="directive",
            staff_names=await get_staff_names_for_directive(directive.id, db)
        ))

    return sorted(tasks, key=lambda t: (
        t.days_remaining is None,
        t.days_remaining if t.days_remaining is not None else 999
    ))
