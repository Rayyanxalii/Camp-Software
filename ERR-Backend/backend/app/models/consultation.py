from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String, Text, Float
)
from app.database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    consultation_id = Column(Integer, primary_key=True)
    registration_id = Column(Integer, ForeignKey("registrations.registration_id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    
    diagnosis = Column(Text, nullable=False)
    prescription = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self):
        return (
            f"<Consultation id={self.consultation_id},"
            f"Registration={self.registration_id}, "
            f"Doctor={self.doctor_id}>"
        )