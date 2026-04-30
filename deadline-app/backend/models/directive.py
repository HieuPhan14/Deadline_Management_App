from sqlalchemy import UniqueConstraint, Table, Column, String, Boolean, DateTime, Integer, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from uuid import uuid4
from datetime import datetime, timezone

directive_assignees = Table(
    "directive_assignees",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("directive_id", UUID(as_uuid=True), ForeignKey("directives.id", ondelete="CASCADE"), nullable=False),
    Column("staff_id", UUID(as_uuid=True), ForeignKey("staff.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("directive_id", "staff_id", name="uq_directive_staff")
)

class Directive(Base):
    __tablename__ = "directives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    row_number = Column(Integer)
    meeting_date = Column(Date)
    directive_content = Column(Text)
    deadline = Column(Date)
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurrence_label = Column(String)
    status = Column(String, nullable=False, default="pending")
    result = Column(Text)
    notes = Column(Text)
    imported_at = Column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc))
    imported_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    def is_overdue(self) -> bool:
        ...

    def days_remaining(self) -> int:
        ...

    def urgency_tier(self) -> str:
        ...

    def mark_done(self) -> None:
        ...

    def mark_in_progress(self) -> None:
        ...