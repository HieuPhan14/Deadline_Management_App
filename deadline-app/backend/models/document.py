from sqlalchemy import Table, Column, String, Boolean, DateTime, Integer, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from uuid import uuid4
from datetime import datetime, timezone

document_assignees = Table(
    "document_assignees",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("document_id", UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
    Column("staff_id", UUID(as_uuid=True), ForeignKey("staff.id", ondelete="CASCADE"), nullable=False),
)

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    row_number = Column(Integer)
    received_date = Column(Date)
    document_type = Column(String)
    content_summary = Column(Text)
    reference_number = Column(String)
    requirement = Column(Text)
    deadline = Column(Date)
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurrence_label = Column(String)
    status = Column(String, nullable=False, default="pending")
    notes = Column(Text)
    imported_at = Column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc))
    imported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

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