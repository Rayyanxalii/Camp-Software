from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.schemas.medicine import MedicineAvailabilityResponse


def get_all_available_medicines(db: Session):

    medicines = db.query(Inventory).all()

    return [
        MedicineAvailabilityResponse(
            medicine_id=medicine.medicine_id,
            medicine_name=medicine.medicine_name,
            strength=medicine.strength,
            dosage_form=medicine.dosage_form,
            available_quantity=medicine.quantity - medicine.reserved_quantity
        )
        for medicine in medicines
    ]       