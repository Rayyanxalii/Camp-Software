"""Stock/Pharmacy router - handles Medicine and Inventory management"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Medicine, Inventory, Users
from app.schemas.stock import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse,
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    StockAddRequest,
    StockDeductRequest,
    LowStockResponse,
    StockImportRequest,
)
from app.dependencies import get_current_active_user

router = APIRouter()

# Default threshold for low stock alerts
LOW_STOCK_THRESHOLD = 10


# ─────────────────────────────────────────────
# Medicine endpoints
# ─────────────────────────────────────────────

@router.get("/medicines", response_model=list[MedicineResponse])
async def list_medicines(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all medicines with pagination

    Returns:
        List of medicines
    """
    medicines = db.query(Medicine).offset(skip).limit(limit).all()
    return medicines


@router.get("/medicines/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(
    medicine_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a medicine by ID

    Raises:
        HTTPException: If medicine not found
    """
    medicine = db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()

    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine {medicine_id} not found"
        )
    return medicine


@router.post("/medicines", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    data: MedicineCreate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a new medicine to the formulary

    Raises:
        HTTPException: If medicine with same name+strength already exists
    """
    existing = db.query(Medicine).filter(
        Medicine.medicine_name == data.medicine_name,
        Medicine.strength == data.strength,
        Medicine.Form == data.Form
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine with this name, strength, and form already exists"
        )

    new_medicine = Medicine(**data.model_dump())
    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)
    return new_medicine


@router.put("/medicines/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
    medicine_id: int,
    data: MedicineUpdate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a medicine record"""
    medicine = db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()

    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine {medicine_id} not found"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(medicine, field, value)

    db.commit()
    db.refresh(medicine)
    return medicine


@router.delete("/medicines/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicine(
    medicine_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a medicine"""
    medicine = db.query(Medicine).filter(Medicine.medicine_id == medicine_id).first()

    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine {medicine_id} not found"
        )

    db.delete(medicine)
    db.commit()


# ─────────────────────────────────────────────
# Inventory endpoints
# ─────────────────────────────────────────────

@router.get("/inventory", response_model=list[InventoryResponse])
async def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all inventory entries"""
    return db.query(Inventory).offset(skip).limit(limit).all()


@router.get("/inventory/low-stock")
async def get_low_stock(
    threshold: int = Query(LOW_STOCK_THRESHOLD, ge=0),
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get inventory entries below the stock threshold

    Args:
        threshold: Minimum stock level (default: 10)

    Returns:
        List of low-stock items with medicine info
    """
    low_stock_items = db.query(Inventory, Medicine).join(
        Medicine, Inventory.medicine_id == Medicine.medicine_id
    ).filter(
        Inventory.current_stock <= threshold
    ).all()

    return [
        {
            "inventory_id": inv.inventory_id,
            "medicine_id": med.medicine_id,
            "medicine_name": med.medicine_name,
            "current_stock": inv.current_stock,
        }
        for inv, med in low_stock_items
    ]


@router.get("/inventory/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(
    inventory_id: int,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get an inventory entry by ID"""
    inventory = db.query(Inventory).filter(
        Inventory.inventory_id == inventory_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory entry {inventory_id} not found"
        )
    return inventory


@router.post("/inventory", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    data: InventoryCreate,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an inventory entry for a medicine

    Raises:
        HTTPException: If medicine not found or inventory already exists for it
    """
    if not db.query(Medicine).filter(Medicine.medicine_id == data.medicine_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medicine {data.medicine_id} not found"
        )

    existing = db.query(Inventory).filter(
        Inventory.medicine_id == data.medicine_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inventory entry already exists for this medicine. Use add/deduct endpoints."
        )

    new_inventory = Inventory(**data.model_dump())
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    return new_inventory


@router.post("/inventory/add", response_model=InventoryResponse)
async def add_stock(
    data: StockAddRequest,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add stock to an existing inventory entry

    Raises:
        HTTPException: If inventory for medicine not found
    """
    inventory = db.query(Inventory).filter(
        Inventory.medicine_id == data.medicine_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No inventory found for medicine {data.medicine_id}"
        )

    inventory.current_stock += data.quantity
    db.commit()
    db.refresh(inventory)
    return inventory


@router.post("/inventory/deduct", response_model=InventoryResponse)
async def deduct_stock(
    data: StockDeductRequest,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deduct stock from an existing inventory entry

    Raises:
        HTTPException: If inventory not found or insufficient stock
    """
    inventory = db.query(Inventory).filter(
        Inventory.medicine_id == data.medicine_id
    ).first()

    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No inventory found for medicine {data.medicine_id}"
        )

    if inventory.current_stock < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {inventory.current_stock}, Requested: {data.quantity}"
        )

    inventory.current_stock -= data.quantity
    db.commit()
    db.refresh(inventory)
    return inventory


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_stock(
    import_data: StockImportRequest,
    current_user: Users = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Bulk import medicines with initial stock levels

    Returns:
        Import summary with counts and errors
    """
    created_count = 0
    errors = []

    for item in import_data.items:
        try:
            # Check if medicine already exists
            existing = db.query(Medicine).filter(
                Medicine.medicine_name == item.medicine_name,
                Medicine.strength == item.strength,
                Medicine.Form == item.Form
            ).first()

            if existing:
                errors.append(
                    f"Medicine '{item.medicine_name}' ({item.strength}, {item.Form}) already exists"
                )
                continue

            # Create medicine
            medicine = Medicine(
                medicine_name=item.medicine_name,
                strength=item.strength,
                Form=item.Form,
                manufacturer=item.manufacturer,
            )
            db.add(medicine)
            db.flush()  # get medicine_id without full commit

            # Create inventory entry
            inventory = Inventory(
                medicine_id=medicine.medicine_id,
                current_stock=item.initial_stock,
            )
            db.add(inventory)
            created_count += 1

        except Exception as e:
            errors.append(f"Error importing '{item.medicine_name}': {str(e)}")

    db.commit()

    return {
        "created": created_count,
        "total": len(import_data.items),
        "errors": errors,
    }
