from pydantic import BaseModel
from app.models.User import UserRole


class CreateUserRequest(BaseModel):
    login_id: str
    password: str
    role: UserRole
    

class UserResponse(BaseModel):
    user_id: int
    login_id: str
    role: UserRole

    class Config:
        from_attributes = True