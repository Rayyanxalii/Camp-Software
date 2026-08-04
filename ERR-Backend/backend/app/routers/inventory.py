from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import UploadFile, File


from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse
from app.database import get_db
from app.dependencies.roles import require_admin
from app.services.inventory_service import create_inventory,get_all_inventory,update_inventory,get_medicine_by_name, delete_inventory, upload_inventory_excel


router = APIRouter(
    prefix = "/inventory",
    tags =["Inventory"]    
)


@router.post(
    '',
    response_model = InventoryResponse
)
def create_inventory_endpoint(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    user = Depends(require_admin)
):
    
    return create_inventory(db, inventory)
    


@router.get(
    "",
    response_model=list[InventoryResponse]
)
def get_inventory_endpoint(
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return get_all_inventory(db)



@router.get(
    "/search/{medicine_name}",
    response_model=list[InventoryResponse]
)
def search_inventory_endpoint(
    medicine_name: str,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return get_medicine_by_name(db, medicine_name)




@router.put(
    "/{medicine_id}",
    response_model=InventoryResponse
)
def update_inventory_endpoint(
    medicine_id: int,
    medicine: InventoryUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return update_inventory(
        db=db,
        medicine_id=medicine_id,
        medicine_data=medicine,
    ) 


@router.delete(
    "/{medicine_id}"
)
def delete_inventory_endpoint(
    medicine_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return delete_inventory(db, medicine_id)




@router.post("/upload")
def upload_inventory(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return upload_inventory_excel(db, file)