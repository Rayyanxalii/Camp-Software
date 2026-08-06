from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.pharmacy import PharmacyPrescription, DispenseRequest
from app.dependencies.roles import require_pharmacist
from app.services.pharmacy_service import get_prescription_by_token,dispense_medicine



router = APIRouter(
    prefix="/pharmacy",
    tags=["medicine dispatching"]
)


@router.get(
    '/get_consultations',
    response_model = PharmacyPrescription
)
def get_counsultations(
    request = DispenseRequest,
    db: Session = Depends(get_db),
    pharmacist = Depends(require_pharmacist)
):
    
    return get_prescription_by_token(db,request)




@router.post(
    '/dispense'
)
def get_counsultations(
    db: Session = Depends(get_db),
    request = DispenseRequest,
    pharmacist = Depends(require_pharmacist)
):
    
    return dispense_medicine(db,request,pharmacist)