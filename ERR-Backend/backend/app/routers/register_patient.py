from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.register_patient import RegisterPatientRequest, PatientRegistrationResponse
from app.services.registration_service import register_patient
from app.models.User import User
from app.dependencies.roles import require_receptionist


router = APIRouter(
    prefix="/register_patient",
    tags=["Register Patient"]
)


@router.post(
    "",
    response_model=PatientRegistrationResponse
)
def register_new_patient(
    request: RegisterPatientRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_receptionist)
):
    return register_patient(db, request)