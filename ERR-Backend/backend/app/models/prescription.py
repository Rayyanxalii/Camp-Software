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
    medicine_id = Column(Integer, ForeignKey("inventory.medicine_id"), nullable=False)
    
    # dosage = Column(String(50), nullable=False) # "2 tablets", "10 ml"
   
    dispense_quantity = Column(Integer, nullable=False)
    frequency = Column(String(30), nullable=False)       # "1-1-1"
    duration_days = Column(Integer, nullable=False)      # 5
    instructions = Column(Text, nullable=True)           # After meals, Before sleep, etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("consultation_id", "medicine_id", name="uq_consultation_medicine"),
    )

    def __repr__(self):
        return (
            f"<Prescription id={self.prescription_id},"
            f"Consultation={self.consultation_id}, "
            f"Medication={self.medication_name}>"
        )
        
        
    
