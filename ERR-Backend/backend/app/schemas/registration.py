from pydantic import BaseModel, Field
from datetime import date
from app.models.Patient import GenderEnum
from typing import Optional


# this data will be sent by frontend at the time of registring patient
class RegsiterPatient(BaseModel):
    name: str = Field(..., lt = 500, description="Patient's full name")
    date_of_birth: date = Field(..., description="Patient's date of birth")
    gender: GenderEnum = Field(..., description="Patient's gender")
    national_id: Optional[str] = Field(default = None, pattern=r"^\d{11}$", description="Patient's national ID")
    phone: Optional[int] = Field(default = None, description="Patient's phone number")
    address: Optional[str] = Field(default = None, description="Patient's address")
    notes: Optional[str] = Field(default = None, description="Patient's notes")
    

