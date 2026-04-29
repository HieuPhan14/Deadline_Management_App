from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from uuid import uuid4
from datetime import datetime, timezone
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)   
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="admin")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def verify_password(self, plain: str) -> bool:
        return pwd_context.verify(plain, self.hashed_password)

    def is_admin(self) -> bool:
        return self.role in ("admin", "super_admin")

    def is_super_admin(self) -> bool:
        return self.role == "super_admin"