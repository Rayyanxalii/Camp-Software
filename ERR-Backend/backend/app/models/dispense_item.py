from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base


class DispenseItem(Base):

    __tablename__ = "dispense_items"

    dispense_item_id = Column(Integer, primary_key=True)

    dispense_id = Column(
        Integer,
        ForeignKey("dispenses.dispense_id"),
        nullable=False
    )

    prescription_id = Column(
    Integer,
    ForeignKey("prescriptions.prescription_id"),
    nullable=False
)

    created_at = Column(DateTime, default=datetime.utcnow)