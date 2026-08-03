from pydantic import BaseModel, Field
from typing import Optional

class CreateVitals(BaseModel):
    
    height: Optional[float] = Field(default=None, description="Patient's height in centimeters")
    weight: Optional[float] = Field(default=None, description="Patient's weight in kilograms")
    blood_pressure: Optional[str] = Field(default=None, description="Patient's blood pressure in the format 'systolic/diastolic'")
    heart_rate: Optional[int] = Field(default=None, description="Patient's heart rate in beats per minute")
    temperature: Optional[float] = Field(default=None, description="Patient's body temperature in Celsius")
    respiratory_rate: Optional[int] = Field(default=None, description="Patient's respiratory rate in breaths per minute")
    
    history : Optional[str] = Field(default=None, description="Any relevant medical history related to the patient's vitals")
    Additional_Notes: Optional[str] = Field(default=None, description="Any additional notes related to the patient's vitals")