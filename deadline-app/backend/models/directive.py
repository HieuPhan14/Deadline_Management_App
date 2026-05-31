from sqlalchemy import UniqueConstraint, Table, Column, String, Boolean, DateTime, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from database import Base
from uuid import UUID, uuid4
from datetime import date, datetime, timezone


directive_assignees = Table(
    "directive_assignees",
    Base.metadata,
    Column("id", PgUUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("directive_id", PgUUID(as_uuid=True), ForeignKey("directives.id", ondelete="CASCADE"), nullable=False),
    Column("staff_id", PgUUID(as_uuid=True), ForeignKey("staff.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("directive_id", "staff_id", name="uq_directive_staff")
)


class Directive(Base):
    __tablename__ = "directives"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meeting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    directive_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recurrence_label: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    imported_by: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

