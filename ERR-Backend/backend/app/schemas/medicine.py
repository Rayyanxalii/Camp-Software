from pydantic import BaseModel
from typing import Optional


class MedicineAvailabilityResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    strength: Optional[str] = None
    dosage_form: str
    available_quantity: int

    class Config:
        from_attributes = True