from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.database import get_db
from app.schemas.vitals import VitalsResponse, CreateVitals
from app.services.vitals_service import create_vitals
from app.dependencies.roles import require_doctor


router = APIRouter(
    prefix="/vitals",
    tags=["Vitals"],
)


@router.post("/", response_model=VitalsResponse)
def Create_Vitals(
    patient_vitals: CreateVitals,
    db: Session = Depends(get_db),
    current_user=Depends(require_doctor)
):
    
    return create_vitals(db, patient_vitals)