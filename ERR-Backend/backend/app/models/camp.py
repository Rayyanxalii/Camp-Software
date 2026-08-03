from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Date
from app.database import Base


class Camp(Base):
    __tablename__ = "camps"

    id = Column(Integer, primary_key=True)
    camp_name = Column(String(50), nullable = False)
    location = Column(String(100), nullable = False)
    organizer = Column(String(100), nullable = False)
    notes = Column(Text, default = None)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __repr__(self):
        return f"<Camp {self.camp_name} >"