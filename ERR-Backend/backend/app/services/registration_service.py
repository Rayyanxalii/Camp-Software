from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.registration import Registration
from app.models.camp import Camp

from app.schemas.register_patient import RegisterPatientRequest


def register_patient(db: Session, patient_data: RegisterPatientRequest):
    try:

        # ---------------------------------------
        # Check if camp exists
        # ---------------------------------------
        camp = db.query(Camp).filter(
            Camp.id == patient_data.camp_id
        ).first()

        if not camp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camp with ID {patient_data.camp_id} not found"
            )

        # ---------------------------------------
        # Find existing patient (if CNIC provided)
        # ---------------------------------------
        patient = None

        if patient_data.national_id:
            patient = db.query(Patient).filter(
                Patient.national_id == patient_data.national_id
            ).first()

        # ---------------------------------------
        # Create patient if not found
        # ---------------------------------------
        if patient is None:

            patient = Patient(
                name=patient_data.name,
                date_of_birth=patient_data.date_of_birth,
                gender=patient_data.gender,
                national_id=patient_data.national_id,
                phone=patient_data.phone,
                address=patient_data.address,
                notes=patient_data.notes,
            )

            db.add(patient)
            db.flush()      # Gives patient.id without committing

        # ---------------------------------------
        # Check if patient already registered
        # in this camp
        # ---------------------------------------
        existing_registration = db.query(Registration).filter(
            Registration.patient_id == patient.id,
            Registration.camp_id == patient_data.camp_id
        ).first()

        if existing_registration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient is already registered in this camp."
            )

        # ---------------------------------------
        # Generate next token number
        # ---------------------------------------
        last_registration = (
            db.query(Registration)
            .filter(
                Registration.camp_id == patient_data.camp_id
            )
            .order_by(Registration.token_no.desc())
            .first()
        )

        next_token = (
            last_registration.token_no + 1
            if last_registration
            else 1
        )

        # ---------------------------------------
        # Create registration
        # ---------------------------------------
        registration = Registration(
            patient_id=patient.id,
            camp_id=patient_data.camp_id,
            token_no=next_token
        )

        db.add(registration)
        

        # Commit once
        db.commit()

        db.refresh(patient)
        db.refresh(registration)

        return registration


    # Preserve HTTPExceptions (400, 404, etc.)
    except HTTPException:
        db.rollback()
        raise
    

    # Handle unexpected errors
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while registering the patient."
        )