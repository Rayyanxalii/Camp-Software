from datetime import datetime
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Enum
)

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    RECEPTIONIST = "RECEPTIONIST"
    PHARMACIST = "PHARMACIST"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)

    login_id = Column(String(100), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    role = Column(Enum(UserRole), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"