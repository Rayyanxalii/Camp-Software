from sqlalchemy.orm import Session
import logging

from app.models.User import User, UserRole
from app.security import hash_password
from app.config import settings
from app.security import verify_password, create_access_token


def authenticate_user(
    db: Session,
    login_id: str,
    password: str
):
    user = db.query(User).filter(
        User.login_id == login_id
    ).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user


def create_admin_if_not_exists(db: Session):
    admin = db.query(User).filter(
        User.role == UserRole.ADMIN
    ).first()

    if admin:
        return

    # Only create a default admin when explicitly allowed and a password is provided
    if not settings.CREATE_DEFAULT_ADMIN:
        logging.warning("CREATE_DEFAULT_ADMIN is not enabled; skipping default admin creation")
        return

    admin_password = settings.ADMIN_PASSWORD
    if not admin_password:
        logging.warning("CREATE_DEFAULT_ADMIN enabled but ADMIN_PASSWORD not set; skipping admin creation")
        return

    admin = User(
        login_id="admin",
        password_hash=hash_password(admin_password),
        role=UserRole.ADMIN,
        is_active=True
    )

    try:
        db.add(admin)
        db.commit()
    except Exception:
        db.rollback()
        logging.exception("Failed to create default admin")
        raise