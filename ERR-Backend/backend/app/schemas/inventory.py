from pydantic import BaseModel
from typing import Optional


class InventoryCreate(BaseModel):
    medicine_name: str
    strength: str
    dosage_form: str      # Tablet, Syrup, Injection
    quantity: int
    manufacturer : str
    
    
class InventoryUpdate(BaseModel):
    medicine_name: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    quantity: Optional[int] = None
    
    
class InventoryResponse(BaseModel):
    medicine_id: int
    medicine_name: str
    strength: str
    dosage_form: str
    quantity: int

    class Config:
        from_attributes = True
        
