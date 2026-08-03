from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.roles import require_admin

from app.models.User import User

from app.schemas.camp_doctor import (
    CampDoctorCreate,
    CampDoctorResponse
)

from app.services.camp_doctor_service import assign_doctor_to_camp



router = APIRouter(
    prefix="/camp-doctor",
    tags=["Camp Doctor Management"]
)


@router.post(
    "/assign",
    response_model=CampDoctorResponse
)
def assign_doctor(
    request: CampDoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return assign_doctor_to_camp(
        db,
        request
    )