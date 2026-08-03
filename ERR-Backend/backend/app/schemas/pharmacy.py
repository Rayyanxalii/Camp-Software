from pydantic import BaseModel, Field
from typing import Optional



class DispatchMedicine(BaseModel):
    medicine_name: str = Field(..., description="Name of the medicine to be dispatched")
    quantity: int = Field(..., description="Quantity of the medicine to be dispatched")
    notes: Optional[str] = Field(default=None, description="Any additional notes related to the dispatch of the medicine")