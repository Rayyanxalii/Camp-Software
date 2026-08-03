from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username of the user")
    password: str = Field(..., description="Password of the user")
    

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token, usually 'bearer'")
    

class UserResponse(BaseModel):
    user_id: int = Field(..., description="Unique identifier for the user")
    login_id: str = Field(..., description="Login ID of the user")
    role: str = Field(..., description="Role of the user, e.g., 'doctor', 'admin', etc.")


