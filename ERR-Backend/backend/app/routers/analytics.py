"""Analytics router - reporting and insights using the new domain models"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app.models import Patient, Registration, Consultation, Doctor, Camp, Medicine, Inventory, Users
from app.schemas.analytics import (
    AnalyticsSummary,
    DoctorVisitStat,
    VisitByDoctorResponse,
    GenderAgeDistribution,
    GenderAgeDistributionResponse,
    CommonDiagnosisResponse,
)
from app.dependencies import get_current_active_user

router = APIRouter()


def calculate_age(date_of_birth) -> int | None:
    """Helper function to calculate age from date of birth"""
    if not date_of_birth:
        return None
    today = datetime.now()
    return (
        today.year - date_of_birth.year
        - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    )


def get_age_group(age: int | None) -> str:
    """Helper function to categorize age into groups"""
    if age is None:
        return "Unknown"
    if age < 18:
        return "0-18"
    elif age < 35:
        return "18-35"
    elif age < 65:
        return "35-65"
    else:
        return "65+"


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics summary dashboard

    Returns:
        Analytics summary with totals across all domain entities
    """
    total_patients = db.query(func.count(Patient.id)).scalar() or 0
    total_registrations = db.query(func.count(Registration.registration_id)).scalar() or 0
    total_consultations = db.query(func.count(Consultation.consultation_id)).scalar() or 0
    total_medicines = db.query(func.count(Medicine.medicine_id)).scalar() or 0
    total_camps = db.query(func.count(Camp.id)).scalar() or 0

    # Most common diagnosis from consultations
    most_common = db.query(
        Consultation.diagnosis
    ).group_by(
        Consultation.diagnosis
    ).order_by(
        func.count(Consultation.consultation_id).desc()
    ).first()

    most_common_diagnosis = most_common[0] if most_common else None

    return AnalyticsSummary(
        total_patients=total_patients,
        total_registrations=total_registrations,
        total_consultations=total_consultations,
        total_medicines=total_medicines,
        total_camps=total_camps,
        most_common_diagnosis=most_common_diagnosis
    )


@router.get("/consultations-by-doctor", response_model=VisitByDoctorResponse)
async def consultations_by_doctor(
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get consultations grouped by doctor

    Returns:
        Consultation statistics per doctor
    """
    doctor_stats = db.query(
        Doctor.doctor_id,
        Doctor.name,
        Doctor.specialization,
        func.count(Consultation.consultation_id).label("total_consultations"),
        func.count(func.distinct(Registration.patient_id)).label("patient_count")
    ).outerjoin(
        Consultation, Consultation.doctor_id == Doctor.doctor_id
    ).outerjoin(
        Registration, Registration.registration_id == Consultation.registration_id
    ).group_by(
        Doctor.doctor_id,
        Doctor.name,
        Doctor.specialization
    ).order_by(
        func.count(Consultation.consultation_id).desc()
    ).all()

    data = [
        DoctorVisitStat(
            doctor_id=stat[0],
            doctor_name=stat[1],
            specialization=stat[2],
            total_consultations=stat[3] or 0,
            patient_count=stat[4] or 0,
        )
        for stat in doctor_stats
    ]

    return VisitByDoctorResponse(
        data=data,
        total_doctors=len(data)
    )


@router.get("/gender-age-distribution", response_model=GenderAgeDistributionResponse)
async def gender_age_distribution(
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get gender and age distribution of patients

    Returns:
        Gender and age distribution with registration counts
    """
    patients = db.query(Patient).all()

    distribution_map = {}
    for patient in patients:
        gender = str(patient.gender.value) if patient.gender else "Unknown"
        age = calculate_age(patient.date_of_birth)
        age_group = get_age_group(age)

        key = (gender, age_group)
        if key not in distribution_map:
            distribution_map[key] = {"patient_count": 0, "total_registrations": 0}

        distribution_map[key]["patient_count"] += 1

        # Count registrations for this patient
        reg_count = db.query(func.count(Registration.registration_id)).filter(
            Registration.patient_id == patient.id
        ).scalar() or 0
        distribution_map[key]["total_registrations"] += reg_count

    data = [
        GenderAgeDistribution(
            gender=key[0],
            age_group=key[1],
            patient_count=value["patient_count"],
            total_registrations=value["total_registrations"]
        )
        for key, value in distribution_map.items()
    ]

    total_patients = sum(item.patient_count for item in data)

    return GenderAgeDistributionResponse(
        data=data,
        total_patients=total_patients
    )


@router.get("/common-diagnoses")
async def get_common_diagnoses(
    limit: int = Query(10, ge=1, le=50),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get most common diagnoses from consultation records

    Returns:
        List of common diagnoses with counts and percentages
    """
    total_consultations = db.query(func.count(Consultation.consultation_id)).scalar() or 1

    common_diagnoses = db.query(
        Consultation.diagnosis,
        func.count(Consultation.consultation_id).label("count")
    ).filter(
        Consultation.diagnosis.isnot(None)
    ).group_by(
        Consultation.diagnosis
    ).order_by(
        func.count(Consultation.consultation_id).desc()
    ).limit(limit).all()

    results = [
        CommonDiagnosisResponse(
            diagnosis_name=item[0],
            count=item[1],
            percentage=round((item[1] / total_consultations) * 100, 2)
        )
        for item in common_diagnoses
    ]

    return {"data": results, "total": len(results)}


@router.get("/medicine-stock")
async def get_medicine_stock_overview(
    limit: int = Query(10, ge=1, le=50),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get medicine inventory overview

    Returns:
        List of medicines with current stock levels
    """
    stock_overview = db.query(
        Medicine.medicine_id,
        Medicine.medicine_name,
        Medicine.strength,
        Inventory.current_stock,
    ).outerjoin(
        Inventory, Inventory.medicine_id == Medicine.medicine_id
    ).order_by(
        Inventory.current_stock.asc()
    ).limit(limit).all()

    results = [
        {
            "medicine_id": item[0],
            "medicine_name": item[1],
            "strength": item[2],
            "current_stock": item[3] if item[3] is not None else 0,
        }
        for item in stock_overview
    ]

    return {"data": results, "total": len(results)}
