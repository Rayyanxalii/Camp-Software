from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.User import User, UserRole


def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user


def require_receptionist(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.RECEPTIONIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Receptionist access required"
        )

    return current_user


def require_doctor(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor access required"
        )

    return current_user