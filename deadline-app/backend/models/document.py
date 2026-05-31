from sqlalchemy import UniqueConstraint, Table, Column, String, Boolean, DateTime, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from database import Base
from uuid import UUID, uuid4
from datetime import date, datetime, timezone


document_assignees = Table(
    "document_assignees",
    Base.metadata,
    Column("id", PgUUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("document_id", PgUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
    Column("staff_id", PgUUID(as_uuid=True), ForeignKey("staff.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("document_id", "staff_id", name="uq_document_staff")
)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    received_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_type: Mapped[str | None] = mapped_column(String, nullable=True)
    content_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String, nullable=True)
    requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recurrence_label: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    imported_by: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

