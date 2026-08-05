from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.prescription import PrescriptionItem


class CreateConsultation(BaseModel):

    token_no: int

    diagnosis: str

    notes: Optional[str] = None

    medicines: list[PrescriptionItem]
    


class ConsultationResponse(BaseModel):

    consultation_id: int
    registration_id: int
    camp_doctor_id: int
    diagnosis: str
    notes: Optional[str]

    class Config:
        from_attributes = True