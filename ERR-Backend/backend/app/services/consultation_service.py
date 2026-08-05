from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.registration import Registration
from app.models.vitals import Vitals
from app.models.consultation import Consultation
from app.models.prescription import Prescription
from app.models.inventory import Inventory
from app.models.camp_doctor import CampDoctor

from app.schemas.consultation import CreateConsultation


def create_consultation(
    db: Session,
    consultation_data: CreateConsultation,
    doctor
):
    try:

        # Get logged-in doctor's camp assignment
        camp_doctor = (
            db.query(CampDoctor)
            .filter(CampDoctor.user_id == doctor.user_id)
            .first()
        )

        if not camp_doctor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor is not assigned to this camp."
            )

        # Find patient registration
        registration = (
            db.query(Registration)
            .filter(
                Registration.camp_id == camp_doctor.camp_id,
                Registration.token_no == consultation_data.token_no
            )
            .first()
        )

        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration not found."
            )

        # Check vitals exist
        vitals = (
            db.query(Vitals)
            .filter(
                Vitals.registration_id == registration.registration_id
            )
            .first()
        )

        if not vitals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient vitals have not been recorded."
            )

        # Prevent duplicate consultation
        existing = (
            db.query(Consultation)
            .filter(
                Consultation.registration_id == registration.registration_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Consultation for this patient already exists."
            )

        # -----------------------------
        # Check and reserve medicines
        # -----------------------------
        for medicine in consultation_data.medicines:

            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.medicine_id == medicine.medicine_id
                )
                .first()
            )

            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Medicine ID {medicine.medicine_id} not found."
                )

            # Check available stock
            if inventory.available_quantity < medicine.dispense_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Only {inventory.available_quantity} "
                        f"{inventory.medicine_name} available."
                    )
                )

            # Reserve stock
            inventory.reserved_quantity += medicine.dispense_quantity

        # -----------------------------
        # Create consultation
        # -----------------------------
        consultation = Consultation(
            registration_id=registration.registration_id,
            camp_doctor_id=camp_doctor.camp_doctor_id,
            diagnosis=consultation_data.diagnosis,
            notes=consultation_data.notes,
        )

        db.add(consultation)
        db.flush()

        # -----------------------------
        # Create prescriptions
        # -----------------------------
        for medicine in consultation_data.medicines:

            prescription = Prescription(
                consultation_id=consultation.consultation_id,
                medicine_id=medicine.medicine_id,
                dispense_quantity=medicine.dispense_quantity,
                frequency=medicine.frequency,
                duration_days=medicine.duration_days,
            )

            db.add(prescription)

        db.commit()
        db.refresh(consultation)

        return consultation

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )