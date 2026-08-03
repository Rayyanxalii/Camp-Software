"""Patients router"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

from app.database import get_db
from app.models import Patient, Users
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientSearchResponse,
    PatientDetailResponse
)
from app.dependencies import get_current_active_user

router = APIRouter()


@router.get("", response_model=list[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all patients with pagination

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of patients
    """
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/search", response_model=list[PatientSearchResponse])
async def search_patients(
    query: str = Query(..., min_length=1),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search patients by name or national ID

    Args:
        query: Search query (matched against name and national_id)
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of matching patients
    """
    search_term = f"%{query}%"

    # name is a String column — use ilike directly
    # national_id is Integer — cast to String for partial matching
    patients = db.query(Patient).filter(
        Patient.name.ilike(search_term)
        | cast(Patient.national_id, String).ilike(search_term)
    ).all()

    return patients


@router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient(
    patient_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a patient by ID

    Args:
        patient_id: Patient ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Patient details

    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )

    return patient


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new patient

    Args:
        patient_data: Patient creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created patient

    Raises:
        HTTPException: If national_id already exists
    """
    # Check if patient with same national_id exists
    existing = db.query(Patient).filter(
        Patient.national_id == patient_data.national_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this national ID already exists"
        )

    # Create new patient
    new_patient = Patient(**patient_data.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a patient

    Args:
        patient_id: Patient ID
        patient_data: Patient update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated patient

    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )

    # Update only provided fields
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a patient

    Args:
        patient_id: Patient ID
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: If patient not found
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )

    db.delete(patient)
    db.commit()
