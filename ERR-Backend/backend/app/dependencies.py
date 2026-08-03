"""FastAPI dependencies for authentication and authorization"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import logging
from typing import Optional

from app.database import get_db
from app.security import decode_token
from app.models import Users
from app.schemas.auth import CurrentUser

logger = logging.getLogger(__name__)


async def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> Users:
    """
    Dependency to get the current authenticated user

    Args:
        db: Database session
        authorization: Authorization header

    Returns:
        Current authenticated Users instance

    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from header (format: "Bearer <token>")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Users = Depends(get_current_user)
) -> Users:
    """
    Dependency to get the current user (kept for API compatibility).

    Args:
        current_user: Current authenticated user

    Returns:
        Current Users instance
    """
    return current_user


async def get_current_admin_user(
    current_user: Users = Depends(get_current_active_user)
) -> Users:
    """
    Dependency to ensure current user has admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if role is 'admin'

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required."
        )
    return current_user


def require_role(role_name: str):
    """
    Dependency factory to require a specific role.

    Args:
        role_name: Name of the required role (e.g., 'admin', 'doctor', 'nurse')

    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: Users = Depends(get_current_active_user)
    ) -> Users:
        """Check if user has the required role"""
        if current_user.role != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' required"
            )
        return current_user

    return role_checker
