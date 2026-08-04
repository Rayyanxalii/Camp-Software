from pydantic import BaseModel, Field
from datetime import date
from app.models.patient import GenderEnum
from typing import Optional


# this data will be sent by frontend at the time of registring patient
class RegisterPatientRequest(BaseModel):

    camp_id: int = Field(..., gt=0, description="Camp ID")

    name: str = Field(..., max_length=255, description="Patient's full name")

    date_of_birth: Optional[date] = None

    gender: GenderEnum

    national_id: Optional[str] = Field(
        default=None,
        pattern=r"^\d{13}$",
        description="Patient's national ID"
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Patient's phone number"
    )

    address: Optional[str] = None

    notes: Optional[str] = None
    


class PatientRegistrationResponse(BaseModel):
    registration_id: int
    patient_id: int
    camp_id: int
    token_no: int

    class Config:
        from_attributes = True