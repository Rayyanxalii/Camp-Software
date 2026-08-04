from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vitals import Vitals
from app.models.registration import Registration
from app.schemas.vitals import CreateVitals


def create_vitals( db: Session , patient_vitals : CreateVitals):
    
    register_valid = db.query(Registration).filter(
    Registration.camp_id == patient_vitals.camp_id,
    Registration.token_no == patient_vitals.token_no
        ).first()
    

    if not register_valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    vitals_exist = db.query(Vitals).filter(Vitals.registration_id == register_valid.registration_id).first()
    
    if vitals_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vitals for this registration already exist"
        )
    
    new_vitals = Vitals(
    registration_id=register_valid.registration_id,
    blood_pressure=patient_vitals.blood_pressure,
    heart_rate=patient_vitals.heart_rate,
    respiratory_rate=patient_vitals.respiratory_rate,
    temperature=patient_vitals.temperature,
    weight=patient_vitals.weight,
    history=patient_vitals.history
)
    
    db.add(new_vitals)
    db.commit()
    db.refresh(new_vitals)
    
    return new_vitals
    