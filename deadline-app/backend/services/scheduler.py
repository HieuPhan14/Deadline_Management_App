from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from database import SessionLocal
from models.document import Document
from models.directive import Directive
from models.audit_log import AuditLog
from datetime import date, datetime, timezone
from uuid import uuid4

scheduler = BackgroundScheduler()
CHECK_INTERVAL_SECONDS = 3600      #1 hour

def check_deadlines():
    db: Session = SessionLocal()
    try:
        today = date.today()
        updated_count = 0

        #check document
        overdue_docs = db.query(Document).filter(
            Document.status.in_(["pending", "in_progress"]),
            Document.deadline < today,
            Document.is_recurring == False,
            Document.deadline.isnot(None)
        ).all()

        for doc in overdue_docs:
            old_status = doc.status
            doc.status = "overdue"

            audit = AuditLog(
                id=uuid4(),
                table_name="documents",
                record_id=doc.id,
                action="update",
                old_values={"status": old_status},
                new_values={"status": "overdue"},
                changed_by=None, #system action, no user
                changed_at=datetime.now(timezone.utc)
            )
            db.add(audit)
            updated_count += 1

        #check directives
        overdue_dirs = db.query(Directive).filter(
            Directive.status.in_(["pending", "in_progress"]),
            Directive.deadline < today,
            Directive.is_recurring == False,
            Directive.deadline.isnot(None)
        ).all()

        for directive in overdue_dirs:
            old_status = directive.status
            directive.status = "overdue"

            audit = AuditLog(
                id=uuid4(),
                table_name="directives",
                record_id=directive.id,
                action="update",
                old_values={"status": old_status},
                new_values={"status": "overdue"},
                changed_by=None, #system action, no user
                changed_at=datetime.now(timezone.utc)
            )
            db.add(audit)
            updated_count += 1

        db.commit()
        print(f"[Scheduler] check deadlines ran - {updated_count} tasks marked overdue")
    
    except Exception as e:
        print(f"[Scheduler] Error: {e}")
        db.rollback()
    finally:
        db.close()

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

