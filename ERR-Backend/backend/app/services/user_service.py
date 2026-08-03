from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.User import User
from app.schemas.user import CreateUserRequest
from app.security import hash_password


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

    hashed_password = hash_password(request.password)

    new_user = User(
        login_id=request.login_id,
        password_hash=hashed_password,
        role=request.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user