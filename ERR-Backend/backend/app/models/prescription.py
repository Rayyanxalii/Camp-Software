from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String, Text,
    UniqueConstraint,
)
from app.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    prescription_id = Column(Integer, primary_key=True)
    
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.medicine_id"), nullable=False)
    
    medication_name = Column(String(100), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)
    duration = Column(String(100), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("consultation_id", "medication_name", name="uq_consultation_medication"),
    )

    def __repr__(self):
        return (
            f"<Prescription id={self.prescription_id},"
            f"Consultation={self.consultation_id}, "
            f"Medication={self.medication_name}>"
        )