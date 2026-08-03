from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String, Text, Float
)
from app.database import Base


class Vitals(Base):
    __tablename__ = "vitals"

    vital_id = Column(Integer, primary_key=True)
    registration_id = Column(Integer, ForeignKey("registrations.registration_id"), nullable=False, unique = True )

    blood_pressure = Column(String(20), nullable=False)
    heart_rate = Column(String(20), nullable=False)
    respiratory_rate = Column(String(20), nullable=False)
    temperature = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    
    history = Column(Text, nullable=True)
    

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self):
        return (
            f"<Vitals id={self.vital_id},"
            f"Registration={self.registration_id}, "
            f"Doctor={self.doctor_id}>"
        )