from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from uuid import uuid4
from datetime import datetime, timezone

class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_tab = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    rows_imported = Column(Integer, nullable=False, default=0)
    rows_skipped = Column(Integer, nullable=False, default=0)
    rows_flagged = Column(Integer, nullable=False, default=0)
    imported_at = Column(DateTime(timezone=True), nullable=False, default=lambda:datetime.now(timezone.utc))
    imported_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    def __repr__(self) -> str:
        return f"<ImportLog {self.filename} {self.imported_at}>"