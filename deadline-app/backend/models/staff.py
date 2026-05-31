from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from database import Base
from uuid import UUID, uuid4
from datetime import datetime, timezone


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    department: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def get_task_count(self) -> int:
        ...

    def get_pending_tasks(self) -> list:
        ...

    def get_overdue_tasks(self) -> list:
        ...

    def __repr__(self) -> str:
        return f"<Staff {self.short_name}>"
