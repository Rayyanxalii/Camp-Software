from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from app.database import Base


class Registration(Base):
    __tablename__ = "registrations"

    registration_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    camp_id = Column(Integer, ForeignKey("camps.id"), nullable=False)
    
    # token number use hoga patient kou identify krnay kay liye camp pr
    token_no = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        UniqueConstraint("camp_id", "token_no", name="uq_camp_token"),
        UniqueConstraint("patient_id", "camp_id", name="uq_patient_camp"),
    )

    def __repr__(self):
        return (
            f"<Registration id={self.registration_id},"
            f"patient={self.patient_id}, "
            f"camp={self.camp_id}>"
        )