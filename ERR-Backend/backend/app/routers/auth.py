from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, Token
from app.services.auth_service import authenticate_user
from app.security import create_access_token
from app.dependencies.auth import get_current_user
from app.models.User import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=Token)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    
    user = authenticate_user(
        db,
        request.login_id,
        request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )

    access_token = create_access_token(
        data={
            "sub": str(user.user_id),
            "role": user.role.value
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 
    
    
@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):  
    return {
        "user_id": current_user.user_id,
        "login_id": current_user.login_id,
        "role": current_user.role
    }
    