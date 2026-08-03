from pydantic import BaseModel, Field
from typing import Optional

class RegisterCamp(BaseModel):
    name: str = Field(..., lt = 500, description="Camp's name")
    location: str = Field(description="Camp's location")
    organizer: str = Field(..., description="Camp's organizer")
    notes: Optional[str] = Field(default = None, description="Any notes related to the camp")
    
