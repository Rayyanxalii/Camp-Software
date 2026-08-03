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


class Medicine(Base):   
    
    __tablename__ = "medicines"
    
    medicine_id = Column(Integer, primary_key=True)
    
    medicine_name = Column(String(100), nullable=False)
    strength = Column(Text, nullable=False)
    Form = Column(String(50), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    
    

def __repr__(self):
        return (
            f"<Medicine id={self.medicine_id},"
            f"Name={self.medicine_name}, "
            f"Strength={self.strength}, "
            f"Form={self.Form}, "
            f"Manufacturer={self.manufacturer}>"
        )