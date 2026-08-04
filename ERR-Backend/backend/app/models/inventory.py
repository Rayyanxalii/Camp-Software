from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    medicine_id = Column(Integer, primary_key=True)

    medicine_name = Column(String(200), nullable=False)
    strength = Column(String(50), nullable=True)      # 500mg
    dosage_form = Column(String(50), nullable=False)  # Tablet, Syrup, Injection
    quantity = Column(Integer, nullable=False)

    manufacturer = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)