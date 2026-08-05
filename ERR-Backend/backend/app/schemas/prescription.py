from pydantic import BaseModel, Field
from typing import Optional


class PrescriptionItem(BaseModel):
    medicine_id: int = Field(...)
    frequency: str = Field(...)
    duration_days: int = Field(..., gt=0)
    instructions : Optional[str] = Field(default = None)
    
    
