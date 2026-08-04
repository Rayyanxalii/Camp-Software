from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
from fastapi import UploadFile

from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate
from app.schemas.inventory import InventoryUpdate



def create_inventory(db: Session, medicine: InventoryCreate):

    existing = db.query(Inventory).filter(
        Inventory.medicine_name == medicine.medicine_name,
        Inventory.strength == medicine.strength,
        Inventory.dosage_form == medicine.dosage_form
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine already exists in inventory."
        )

    new_medicine = Inventory(
        medicine_name=medicine.medicine_name,
        strength=medicine.strength,
        dosage_form=medicine.dosage_form,
        quantity=medicine.quantity,
        manufacturer = medicine.manufacturer
    )

    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)

    return new_medicine




def get_all_inventory(db: Session):

    medicines = db.query(Inventory).all()

    return medicines




def update_inventory(
    db: Session,
    medicine_id: int,
    medicine_data: InventoryUpdate
):
    
    medicine = db.query(Inventory).filter(
        Inventory.medicine_id == medicine_id
    ).first()

    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found."
        )

    update_data = medicine_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(medicine, key, value)

    db.commit()
    db.refresh(medicine)

    return medicine




def get_medicine_by_name(db: Session, medicine_name: str):

    medicines = (
        db.query(Inventory)
        .filter(
            Inventory.medicine_name.ilike(f"%{medicine_name}%")
        ).order_by(Inventory.medicine_name)
        .all()
    )

    if not medicines:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No medicine found."
        )

    return medicines




def delete_inventory(db: Session, medicine_id: int):

    med_exist = db.query(Inventory).filter(
        Inventory.medicine_id == medicine_id
    ).first()

    if not med_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found."
        )

    db.delete(med_exist)
    db.commit()

    return {
        "message": "Medicine deleted successfully."
    }
    
    




def upload_inventory_excel(db: Session, file: UploadFile):

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel (.xlsx) files are allowed."
        )

    try:

        df = pd.read_excel(file.file)

        added = 0
        skipped = 0

        for _, row in df.iterrows():

            medicine_name = row["medicine_name"]
            strength = row["strength"]
            dosage_form = row["dosage_form"]
            quantity = row["quantity"]
            manufacturer = row.get("manufacturer")

            existing = db.query(Inventory).filter(
                Inventory.medicine_name == medicine_name,
                Inventory.strength == strength,
                Inventory.dosage_form == dosage_form,
                Inventory.manufacturer == manufacturer
            ).first()

            if existing:
                skipped += 1
                continue

            medicine = Inventory(
                medicine_name=medicine_name,
                strength=strength,
                dosage_form=dosage_form,
                quantity=quantity,
                manufacturer=manufacturer
            )

            db.add(medicine)
            added += 1

        db.commit()

        return {
            "message": "Inventory uploaded successfully.",
            "added": added,
            "skipped": skipped
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )