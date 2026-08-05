from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.roles import require_doctor
from app.schemas.medicine import MedicineAvailabilityResponse
from app.services.medicine import get_all_available_medicines

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.get(
    "/available",
    response_model=list[MedicineAvailabilityResponse]
)
def get_available_inventory(
    db: Session = Depends(get_db),
    user=Depends(require_doctor)
):
    return get_all_available_medicines(db)