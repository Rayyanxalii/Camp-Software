from pydantic import BaseModel, Field
from typing import Optional

class CampCreate(BaseModel):
    camp_name: str = Field(...,  max_length=500, description="Camp's name")
    location: str = Field(description="Camp's location")
    organizer: str = Field(..., description="Camp's organizer")
    notes: str = Field(default = None, description="Any notes related to the camp")
    

class CampResponse(BaseModel):
    id: int
    camp_name: str
    location: str
    organizer: str
    
    class Config:
        from_attributes = True