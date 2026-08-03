from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.camp import Camp
from app.models.camp_doctor import CampDoctor
from app.models.User import User
from app.models.User import UserRole   # adjust if your enum is elsewhere

from app.schemas.camp_doctor import CampDoctorCreate


def assign_doctor_to_camp(
    db: Session,
    request: CampDoctorCreate
):
    
    camp = db.query(Camp).filter(
        Camp.id == request.camp_id
    ).first()
    
    if not camp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camp not found"
        )
    
    user = db.query(User).filter(
    User.user_id == request.user_id).first()

    if user is None:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )
        
    if user.role != UserRole.DOCTOR:
     raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Selected user is not a doctor"
    )
     
    existing = db.query(CampDoctor).filter(
        CampDoctor.camp_id == request.camp_id,
        CampDoctor.user_id == request.user_id
        ).first()


    if existing:
     raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Doctor already assigned to this camp"
    )
     
    assignment = CampDoctor(
    camp_id=request.camp_id,
    user_id=request.user_id
)

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment   