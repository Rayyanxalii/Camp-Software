from sqlalchemy.orm import Session

from app.models.camp import Camp
from app.schemas.camp import CampCreate


def create_camp(
    db: Session,
    request: CampCreate
):

    new_camp = Camp(
        camp_name=request.camp_name,
        location=request.location,
        organizer=request.organizer,
        notes = request.notes
        
    )

    db.add(new_camp)
    db.commit()
    db.refresh(new_camp)

    return new_camp