"""
app/api/routes_suppliers.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.common import SupplierOut, SupplierMessageOut
from app.core.deps import get_current_user

router = APIRouter()

_SUPPLIER_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


def get_repo(db: Database = Depends(get_mongo_db)):
    return SupplierRepository(db)


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(
    repo: SupplierRepository = Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """
    GET /suppliers/
    Admin and User roles can see all suppliers.
    Supplier role can only see themselves.
    """
    if current_user["role"] == "supplier":
        supplier_id = current_user.get("supplier_id")
        single = repo.get_by_supplier_id(supplier_id)
        return [single] if single else []
        
    return repo.list_all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(
    supplier_id: str = Path(..., pattern=_SUPPLIER_ID_PATTERN, min_length=1, max_length=32),
    repo: SupplierRepository = Depends(get_repo),
    current_user: dict = Depends(get_current_user),
):
    """
    GET /suppliers/{supplier_id}
    Enforces that suppliers can only request their own details.
    """
    if current_user["role"] == "supplier" and supplier_id != current_user.get("supplier_id"):
        raise HTTPException(status_code=403, detail="Not authorized to access this supplier")

    row = repo.get_by_supplier_id(supplier_id)
    if not row:
        raise HTTPException(status_code=404, detail="supplier not found")
    return row


@router.get("/{supplier_id}/messages", response_model=List[SupplierMessageOut])
def get_supplier_messages(
    supplier_id: str = Path(..., pattern=_SUPPLIER_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
    current_user: dict = Depends(get_current_user),
):
    """
    GET /suppliers/{supplier_id}/messages
    Returns all messages exchanged with this supplier.
    Enforces that suppliers can only request their own messages.
    """
    if current_user["role"] == "supplier" and supplier_id != current_user.get("supplier_id"):
        raise HTTPException(status_code=403, detail="Not authorized to access these messages")

    supplier = SupplierRepository(db).get_by_supplier_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="supplier not found")

    return list(db["supplier_messages"].find({"supplier_id": supplier_id}, {"_id": 0}).sort("timestamp", 1))
