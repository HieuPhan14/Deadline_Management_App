from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base
from uuid import uuid4
from datetime import datetime, timezone

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    table_name = Column(String, nullable=False)
    record_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    changed_at = Column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"<AuditLog {self.table_name} {self.action}>"