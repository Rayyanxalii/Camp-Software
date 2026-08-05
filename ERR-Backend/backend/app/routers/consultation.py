from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.consultation import (
    CreateConsultation,
    ConsultationResponse,
)

from app.dependencies.roles import require_doctor

from app.services.consultation_service import create_consultation


router = APIRouter(
    prefix="/consultations",
    tags=["Consultations"],
)


@router.post(
    "",
    response_model=ConsultationResponse,
)
def create_new_consultation(
    consultation: CreateConsultation,
    db: Session = Depends(get_db),
    doctor=Depends(require_doctor),
):
    return create_consultation(
        db=db,
        consultation_data=consultation,
        doctor=doctor,
    )