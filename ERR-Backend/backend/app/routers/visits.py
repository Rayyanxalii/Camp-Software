"""Visits router - handles patient camp Registrations and Consultations"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Registration, Consultation, Vitals, Patient, Camp, Doctor, Users
from app.schemas.visit import (
    RegistrationCreate,
    RegistrationUpdate,
    RegistrationResponse,
    ConsultationCreate,
    ConsultationUpdate,
    ConsultationResponse,
    VitalsCreate,
    VitalsUpdate,
    VitalsResponse,
)
from app.dependencies import get_current_active_user

router = APIRouter()


# ─────────────────────────────────────────────
# Registration endpoints
# ─────────────────────────────────────────────

@router.get("/registrations", response_model=list[RegistrationResponse])
async def list_registrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    patient_id: int | None = Query(None),
    camp_id: int | None = Query(None),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List patient camp registrations with optional filtering

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        patient_id: Filter by patient ID
        camp_id: Filter by camp ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of registrations
    """
    query = db.query(Registration)

    if patient_id:
        query = query.filter(Registration.patient_id == patient_id)
    if camp_id:
        query = query.filter(Registration.camp_id == camp_id)

    return query.order_by(Registration.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/registrations/{registration_id}", response_model=RegistrationResponse)
async def get_registration(
    registration_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a registration by ID

    Raises:
        HTTPException: If registration not found
    """
    reg = db.query(Registration).filter(
        Registration.registration_id == registration_id
    ).first()

    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration {registration_id} not found"
        )
    return reg


@router.post("/registrations", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    data: RegistrationCreate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Register a patient into a camp

    Raises:
        HTTPException: If patient/camp not found or duplicate registration
    """
    # Verify patient exists
    if not db.query(Patient).filter(Patient.id == data.patient_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {data.patient_id} not found"
        )

    # Verify camp exists
    if not db.query(Camp).filter(Camp.id == data.camp_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camp {data.camp_id} not found"
        )

    new_reg = Registration(**data.model_dump())
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg


@router.put("/registrations/{registration_id}", response_model=RegistrationResponse)
async def update_registration(
    registration_id: int,
    data: RegistrationUpdate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a registration's token number"""
    reg = db.query(Registration).filter(
        Registration.registration_id == registration_id
    ).first()

    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration {registration_id} not found"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(reg, field, value)

    db.commit()
    db.refresh(reg)
    return reg


@router.delete("/registrations/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registration(
    registration_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a registration"""
    reg = db.query(Registration).filter(
        Registration.registration_id == registration_id
    ).first()

    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration {registration_id} not found"
        )

    db.delete(reg)
    db.commit()


# ─────────────────────────────────────────────
# Vitals endpoints
# ─────────────────────────────────────────────

@router.get("/vitals", response_model=list[VitalsResponse])
async def list_vitals(
    registration_id: int | None = Query(None),
    doctor_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List vitals with optional filtering by registration or doctor"""
    query = db.query(Vitals)

    if registration_id:
        query = query.filter(Vitals.registration_id == registration_id)
    if doctor_id:
        query = query.filter(Vitals.doctor_id == doctor_id)

    return query.order_by(Vitals.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/vitals/{vital_id}", response_model=VitalsResponse)
async def get_vitals(
    vital_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get vitals by ID"""
    vitals = db.query(Vitals).filter(Vitals.vital_id == vital_id).first()

    if not vitals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vitals record {vital_id} not found"
        )
    return vitals


@router.post("/vitals", response_model=VitalsResponse, status_code=status.HTTP_201_CREATED)
async def create_vitals(
    data: VitalsCreate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record vitals for a registration"""
    # Verify registration exists
    if not db.query(Registration).filter(
        Registration.registration_id == data.registration_id
    ).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration {data.registration_id} not found"
        )

    # Verify doctor exists
    if not db.query(Doctor).filter(Doctor.doctor_id == data.doctor_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {data.doctor_id} not found"
        )

    new_vitals = Vitals(**data.model_dump())
    db.add(new_vitals)
    db.commit()
    db.refresh(new_vitals)
    return new_vitals


@router.put("/vitals/{vital_id}", response_model=VitalsResponse)
async def update_vitals(
    vital_id: int,
    data: VitalsUpdate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a vitals record"""
    vitals = db.query(Vitals).filter(Vitals.vital_id == vital_id).first()

    if not vitals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vitals record {vital_id} not found"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vitals, field, value)

    db.commit()
    db.refresh(vitals)
    return vitals


@router.delete("/vitals/{vital_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vitals(
    vital_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a vitals record"""
    vitals = db.query(Vitals).filter(Vitals.vital_id == vital_id).first()

    if not vitals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vitals record {vital_id} not found"
        )

    db.delete(vitals)
    db.commit()
