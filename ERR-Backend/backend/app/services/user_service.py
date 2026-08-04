from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.User import User, UserRole
from app.schemas.user import CreateUserRequest
from app.security import hash_password


def _is_strong_password(password: str) -> bool:
    if not password or len(password) < 8:
        return False
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_lower and has_upper and has_digit


def create_user(
    db: Session,
    request: CreateUserRequest
):
    
    existing_user = db.query(User).filter(
        User.login_id == request.login_id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this login ID already exists"
        )

    #Basic password strength validation
    if not _is_strong_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and include upper, lower and digits"
        )

    # Validate role
    if not isinstance(request.role, UserRole):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    hashed_password = hash_password(request.password)

    new_user = User(
        login_id=request.login_id,
        password_hash=hashed_password,
        role=request.role
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    return new_user