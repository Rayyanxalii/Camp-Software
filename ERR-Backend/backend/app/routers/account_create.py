from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import CreateUserRequest, UserResponse
from app.services.user_service import create_user
from app.dependencies.roles import require_admin
from app.models.User import User


router = APIRouter(
    prefix="/account",
    tags=["Account Management"]
)


@router.post(
    "/users",
    response_model=UserResponse
)
def create_new_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return create_user(db, request)