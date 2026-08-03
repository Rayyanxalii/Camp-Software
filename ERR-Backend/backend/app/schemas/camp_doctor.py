from pydantic import BaseModel


class CampDoctorCreate(BaseModel):
    camp_id: int
    user_id: int


class CampDoctorResponse(BaseModel):
    camp_doctor_id: int
    camp_id: int
    user_id: int
    

    class Config:
        from_attributes = True