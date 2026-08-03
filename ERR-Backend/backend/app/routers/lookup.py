"""Lookup router for ICD codes and reference data"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Consultation, Registration, Users
from app.schemas.analytics import ICDSearchResult
from app.dependencies import get_current_active_user

router = APIRouter()

# Sample ICD-10 database (in production, this would be a separate table)
ICD_DIAGNOSES = {
    "J00": {"description": "Acute nasopharyngitis (common cold)", "category": "Respiratory"},
    "J06": {"description": "Acute upper respiratory infections", "category": "Respiratory"},
    "J20": {"description": "Acute bronchitis", "category": "Respiratory"},
    "K21": {"description": "Gastro-esophageal reflux disease", "category": "Digestive"},
    "M79.3": {"description": "Panniculitis, unspecified", "category": "Musculoskeletal"},
    "E11": {"description": "Type 2 diabetes mellitus", "category": "Endocrine"},
    "I10": {"description": "Essential (primary) hypertension", "category": "Circulatory"},
    "K05": {"description": "Gingivitis and periodontal diseases", "category": "Dental"},
    "K02": {"description": "Dental caries", "category": "Dental"},
    "K04": {"description": "Diseases of pulp and periapical tissues", "category": "Dental"},
}

ICD_SYMPTOMS = {
    "R05": {"description": "Fever", "category": "General symptoms"},
    "R06": {"description": "Abnormalities of breathing", "category": "Respiratory"},
    "R07": {"description": "Chest pain", "category": "Circulatory"},
    "R10": {"description": "Abdominal pain", "category": "Digestive"},
    "R51": {"description": "Headache", "category": "Neurological"},
    "R53": {"description": "Malaise and fatigue", "category": "General symptoms"},
    "R61": {"description": "Hyperhidrosis (excessive sweating)", "category": "General symptoms"},
}


@router.get("/icd-diagnosis", response_model=dict)
async def search_icd_diagnosis(
    query: str = Query(..., min_length=1, max_length=255),
    limit: int = Query(10, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search ICD-10 diagnosis codes

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching ICD codes
    """
    query_lower = query.lower()
    results = []

    for code, data in ICD_DIAGNOSES.items():
        if (query_lower in code.lower() or
                query_lower in data["description"].lower()):
            results.append(ICDSearchResult(
                code=code,
                description=data["description"],
                category=data["category"]
            ))
            if len(results) >= limit:
                break

    return {"results": results, "total": len(results)}


@router.get("/icd-symptoms", response_model=dict)
async def search_icd_symptoms(
    query: str = Query(..., min_length=1, max_length=255),
    limit: int = Query(10, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search ICD-10 symptom codes

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching ICD codes
    """
    query_lower = query.lower()
    results = []

    for code, data in ICD_SYMPTOMS.items():
        if (query_lower in code.lower() or
                query_lower in data["description"].lower()):
            results.append(ICDSearchResult(
                code=code,
                description=data["description"],
                category=data["category"]
            ))
            if len(results) >= limit:
                break

    return {"results": results, "total": len(results)}


@router.get("/recent-diagnoses", response_model=dict)
async def get_recent_diagnoses(
    limit: int = Query(20, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get most frequently used diagnoses from consultation records

    Returns:
        List of recent/common diagnoses with usage counts
    """
    recent = db.query(
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
        {
            "description": item[0],
            "usage_count": item[1]
        }
        for item in recent
    ]

    return {"results": results, "total": len(results)}


@router.get("/camp-stats", response_model=dict)
async def get_camp_registration_stats(
    limit: int = Query(20, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get registration counts grouped by camp

    Returns:
        List of camps with patient registration counts
    """
    stats = db.query(
        Registration.camp_id,
        func.count(Registration.registration_id).label("registration_count")
    ).group_by(
        Registration.camp_id
    ).order_by(
        func.count(Registration.registration_id).desc()
    ).limit(limit).all()

    results = [
        {
            "camp_id": item[0],
            "registration_count": item[1]
        }
        for item in stats
    ]

    return {"results": results, "total": len(results)}
