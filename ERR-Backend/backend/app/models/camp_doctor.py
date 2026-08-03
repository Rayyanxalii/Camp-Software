from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base


class CampDoctor(Base):
    __tablename__ = "camp_doctors"

    camp_doctor_id = Column(Integer, primary_key=True)
    camp_id = Column(Integer, ForeignKey("camps.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<CampDoctor id={self.camp_doctor_id},"
            f"Camp={self.camp_id}, "
            f"Doctor={self.doctor_id}>"
        )