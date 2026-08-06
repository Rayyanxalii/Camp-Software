from pydantic import BaseModel
from pydantic import BaseModel
from typing import List


class PharmacyMedicine(BaseModel):
    medicine_id: int
    medicine_name: str
    strength: str | None = None
    dosage_form: str
    dispense_quantity: int
    frequency: str
    duration_days: int
    instructions: str | None = None



# main response schema, this data will be shown to pharmacist when he adds token number of a patient
class PharmacyPrescription(BaseModel):
    patient_name: str
    medicines: List[PharmacyMedicine]
    
    
    
# request schema
class DispenseRequest(BaseModel):
    token_no: int

