"""Patient model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Date
from app.database import Base
import enum


class GenderEnum(str, enum.Enum):
    """Gender enumeration"""
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    
    
class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable = False)
    date_of_birth = Column(Date, default=None)
    gender = Column(Enum(GenderEnum))
    national_id = Column(String(13), unique=True, default=None)
    phone = Column(String(11), nullable = True, default = 0)
    address = Column(Text, nullable = True, default = None)
    notes = Column(Text, nullable = True, default = None)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __repr__(self):
        return f"<Patient {self.name} >"
