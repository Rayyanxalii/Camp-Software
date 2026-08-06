from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base



class Dispense(Base):

    __tablename__ = "dispenses"

    dispense_id = Column(Integer, primary_key=True)

    registration_id = Column(
        Integer,
        ForeignKey("registrations.registration_id"),
        nullable=False
    )

    pharmacist_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    dispensed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )