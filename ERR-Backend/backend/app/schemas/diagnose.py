from pydantic import BaseModel, Field
from typing import Optional


class CreateDiagnose(BaseModel):
    diagnosis: str = Field(..., description="Diagnosis details")
    medicine_prescribed:str = Field(..., description="Details of the medicine prescribed")
    dosage: str = Field(..., description="Dosage information for the prescribed medicine")
    frequency: str = Field(..., description="Frequency of the prescribed medicine")
    duration: str = Field(..., description="Duration for which the prescribed medicine should be taken")
    notes: Optional[str] = Field(default=None, description="Additional notes related to the diagnosis")