from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.consultation import Consultation
from app.models.prescription import Prescription
from app.models.registration import Registration
from app.models.patient import Patient
from app.models.inventory import Inventory
from app.models.dispense import Dispense
from app.models.dispense_item import DispenseItem

from app.schemas.pharmacy import PharmacyMedicine,PharmacyPrescription



def get_prescription_by_token(db:Session , token_no:int):
    
    registration = (
        db.query(Registration)
        .filter(Registration.token_no == token_no)
        .first()
    )
    
    if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token number not found."
            )
    
    
    
    patient = db.query(Patient).filter(
        Patient.id == registration.patient_id
    ). first()
    
    if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found."
            )

   
    
    consultations = (
        db.query(Consultation).filter(
        Consultation.registration_id == registration.registration_id,
        Consultation.is_dispensed == False
        ).all()
    )
    
    
    if not consultations:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No pending consultations for this patient"
        )
        
    
    medicines = []
    
    
    for consultation in consultations:
        
        prescriptions =(
             db.query(Prescription).filter(
            Prescription.consultation_id == consultation.consultation_id
        ).all()
        )
    

        for prescription in prescriptions:
        
            medicine =(
                db.query(Inventory).filter(
                Inventory.medicine_id == prescription.medicine_id
            ).first()
            )
            
            if not medicine:
                raise HTTPException(
                            status_code = status.HTTP_404_NOT_FOUND,
                            detail = "Medicine not found in Inventory"
                        )
            

            medicines.append(
                PharmacyMedicine(
                    medicine_id=medicine.medicine_id,
                    medicine_name=medicine.medicine_name,
                    strength=medicine.strength,
                    dosage_form=medicine.dosage_form,
                    dispense_quantity=prescription.dispense_quantity,
                    frequency=prescription.frequency,
                    duration_days=prescription.duration_days,
                    instructions=prescription.instructions,
    )
)
    
    
    return PharmacyPrescription(
        patient_name = patient.name,
        medicines = medicines
    )
    
    



def dispense_medicine(db : Session , token_no: int, pharmacist):
    
    
    registration = (
            db.query(Registration)
            .filter(Registration.token_no == token_no)
            .first()
        )
        
    if not registration:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Token number not found."
                )
        
    
    consultations = (
            db.query(Consultation).filter(
            Consultation.registration_id == registration.registration_id,
            Consultation.is_dispensed == False
            ).all()
        )
        
        
    if not consultations:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "No pending consultations for this patient"
            )
            
    
    dispense = Dispense(
    registration_id=registration.registration_id,
    pharmacist_id=pharmacist.user_id
)

    db.add(dispense)
    db.flush()   # Generates dispense_id


    for consultation in consultations:

        prescriptions = (
            db.query(Prescription)
            .filter(
                Prescription.consultation_id == consultation.consultation_id
            )
            .all()
        )

        for prescription in prescriptions:

            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.medicine_id == prescription.medicine_id
                )
                .first()
            )

            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Medicine {prescription.medicine_id} not found."
                )

            # Safety check
            if inventory.reserved_quantity < prescription.dispense_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Reserved quantity is incorrect for {inventory.medicine_name}."
                )

            # Update inventory
            inventory.quantity -= prescription.dispense_quantity
            inventory.reserved_quantity -= prescription.dispense_quantity

            # Create dispense item
            dispense_item = DispenseItem(
                dispense_id=dispense.dispense_id,
                prescription_id=prescription.prescription_id
            )

            db.add(dispense_item)

        # Mark this consultation as dispensed
        consultation.is_dispensed = True


    db.commit()
    db.refresh(dispense)

    return {
        "message": "Medicines dispensed successfully.",
        "dispense_id": dispense.dispense_id
    }


    
    