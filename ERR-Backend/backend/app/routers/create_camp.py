from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.camp import CampCreate, CampResponse
from app.services.camp_service import create_camp
from app.dependencies.roles import require_admin


router = APIRouter(
    prefix="/camp",
    tags=["Camps"]
)


@router.post(
    "/create",
    response_model=CampResponse
)
def create_new_camp(
    request: CampCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):

    return create_camp(
        db,
        request
    )
    
