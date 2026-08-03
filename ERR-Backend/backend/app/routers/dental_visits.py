"""Consultations router - handles doctor consultations (replaces dental_visits)"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Consultation, Registration, Doctor, Prescription, Medicine, Users
from app.schemas.visit import (
    ConsultationCreate,
    ConsultationUpdate,
    ConsultationResponse,
)
from app.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=list[ConsultationResponse])
async def list_consultations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    registration_id: int | None = Query(None),
    doctor_id: int | None = Query(None),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List consultations with optional filtering

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        registration_id: Filter by registration ID
        doctor_id: Filter by doctor ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of consultations
    """
    query = db.query(Consultation)

    if registration_id:
        query = query.filter(Consultation.registration_id == registration_id)
    if doctor_id:
        query = query.filter(Consultation.doctor_id == doctor_id)

    return query.order_by(Consultation.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(
    consultation_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a consultation by ID

    Raises:
        HTTPException: If consultation not found
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation {consultation_id} not found"
        )

    return consultation


@router.post("", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
async def create_consultation(
    data: ConsultationCreate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new consultation record

    Args:
        data: Consultation creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created consultation

    Raises:
        HTTPException: If registration or doctor not found
    """
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

    new_consultation = Consultation(**data.model_dump())
    db.add(new_consultation)
    db.commit()
    db.refresh(new_consultation)

    return new_consultation


@router.put("/{consultation_id}", response_model=ConsultationResponse)
async def update_consultation(
    consultation_id: int,
    data: ConsultationUpdate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a consultation record

    Args:
        consultation_id: Consultation ID
        data: Consultation update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated consultation

    Raises:
        HTTPException: If consultation not found
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation {consultation_id} not found"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(consultation, field, value)

    db.commit()
    db.refresh(consultation)

    return consultation


@router.delete("/{consultation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consultation(
    consultation_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a consultation

    Raises:
        HTTPException: If consultation not found
    """
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation {consultation_id} not found"
        )

    db.delete(consultation)
    db.commit()
