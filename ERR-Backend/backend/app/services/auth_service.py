from sqlalchemy.orm import Session
from app.models.User import User, UserRole
from app.security import hash_password
from app.config import Settings
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

    admin = User(
        login_id="admin",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )

    db.add(admin)
    db.commit()