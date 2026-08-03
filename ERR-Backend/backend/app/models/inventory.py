from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True)
    medicine_id = Column(Integer, ForeignKey("medicines.medicine_id"), nullable=False)
    
    current_stock = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<Inventory id={self.inventory_id},"
            f"Medicine={self.medicine_id}, "
            f"Quantity={self.current_stock}>"
        )