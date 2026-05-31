from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from database import AsyncSessionLocal
from models.document import Document
from models.directive import Directive
from models.audit_log import AuditLog
from datetime import date, datetime, timezone
from uuid import uuid4

scheduler = AsyncIOScheduler()
CHECK_INTERVAL_SECONDS = 3600


async def check_deadlines():
    async with AsyncSessionLocal() as db:
        try:
            today = date.today()
            updated_count = 0

            overdue_docs_result = await db.execute(
                select(Document).where(
                    Document.status.in_(["pending", "in_progress"]),
                    Document.deadline < today,
                    Document.is_recurring == False,
                    Document.deadline.isnot(None)
                )
            )
            for doc in overdue_docs_result.scalars().all():
                old_status = doc.status
                doc.status = "overdue"
                db.add(AuditLog(
                    id=uuid4(),
                    table_name="documents",
                    record_id=doc.id,
                    action="update",
                    old_values={"status": old_status},
                    new_values={"status": "overdue"},
                    changed_by=None,
                    changed_at=datetime.now(timezone.utc)
                ))
                updated_count += 1

            overdue_dirs_result = await db.execute(
                select(Directive).where(
                    Directive.status.in_(["pending", "in_progress"]),
                    Directive.deadline < today,
                    Directive.is_recurring == False,
                    Directive.deadline.isnot(None)
                )
            )
            for directive in overdue_dirs_result.scalars().all():
                old_status = directive.status
                directive.status = "overdue"
                db.add(AuditLog(
                    id=uuid4(),
                    table_name="directives",
                    record_id=directive.id,
                    action="update",
                    old_values={"status": old_status},
                    new_values={"status": "overdue"},
                    changed_by=None,
                    changed_at=datetime.now(timezone.utc)
                ))
                updated_count += 1

            await db.commit()
            print(f"[Scheduler] check deadlines ran - {updated_count} tasks marked overdue")

        except Exception as e:
            print(f"[Scheduler] Error: {e}")
            await db.rollback()


def start_scheduler():
    scheduler.add_job(
        func=check_deadlines,
        trigger=IntervalTrigger(seconds=CHECK_INTERVAL_SECONDS),
        id="check_deadlines",
        replace_existing=True
    )
    scheduler.start()
    print(f"[Scheduler] Started - checking deadlines every {CHECK_INTERVAL_SECONDS} seconds")


def stop_scheduler():
    scheduler.shutdown()
    print("[Scheduler] Stopped")
