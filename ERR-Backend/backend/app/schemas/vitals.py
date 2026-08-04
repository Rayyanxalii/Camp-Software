from pydantic import BaseModel, Field
from typing import Optional

class CreateVitals(BaseModel):
    
    camp_id: int = Field(..., description="Camp ID")
    token_no: int = Field(..., description="Patient token number")
    
    weight: Optional[float] = Field(default=None, description="Patient's weight in kilograms")
    blood_pressure: str = Field(..., description="Patient's blood pressure in the format 'systolic/diastolic'")
    heart_rate: Optional[int] = Field(default=None, description="Patient's heart rate in beats per minute")
    temperature: Optional[float] = Field(default=None, description="Patient's body temperature in Celsius")
    respiratory_rate: Optional[int] = Field(default=None, description="Patient's respiratory rate in breaths per minute")
    
    history : Optional[str] = Field(default=None, description="Any relevant medical history related to the patient's vitals")
    

class VitalsResponse(BaseModel):
    vital_id: int
    registration_id: int
    blood_pressure: str
    heart_rate: Optional[int]
    respiratory_rate: Optional[int]
    temperature: Optional[float]
    weight: Optional[float]

    class Config:
        from_attributes = True