from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from uuid import uuid4
from datetime import datetime, timezone

class Staff(Base):
    __tablename__ = "staff"

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    full_name = Column(String, nullable=False)
    short_name = Column(String, nullable=False, unique=True)
    department = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def get_task_count(self) -> int:
        ...

    def get_pending_tasks(self) -> list:
        ...

    def get_overdue_tasks(self) -> list:
        ...

    def __repr__(self) -> str:
        return f"<Staff {self.short_name}>"