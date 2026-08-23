"""
app/api/routes_suppliers.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List, Optional
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.common import SupplierOut, SupplierMessageOut
from app.core.deps import get_current_user

router = APIRouter()

_SUPPLIER_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


def get_repo(db: Database = Depends(get_mongo_db)):
    return SupplierRepository(db)


def _resolve_supplier_id(current_user: dict, db: Database) -> Optional[str]:
    supplier_id = current_user.get("supplier_id")
    if supplier_id:
        return supplier_id
    email = current_user.get("email")
    if email:
        supp = db["suppliers"].find_one({"contact_email": email.lower()})
        if supp:
            return supp.get("supplier_id")
    user_id = current_user.get("user_id")
    if user_id:
        supp = db["suppliers"].find_one({"user_id": user_id})
        if supp:
            return supp.get("supplier_id")
    return None


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(
    db: Database = Depends(get_mongo_db),
    current_user: dict = Depends(get_current_user),
):
    """
    GET /suppliers/
    Admin and User roles can see all suppliers.
    Supplier role can only see themselves.
    """
    repo = SupplierRepository(db)
    if current_user["role"] == "supplier":
        supplier_id = _resolve_supplier_id(current_user, db)
        if not supplier_id:
            return []
        single = repo.get_by_supplier_id(supplier_id)
        return [single] if single else []
        
    return repo.list_all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(
    supplier_id: str = Path(..., pattern=_SUPPLIER_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
    current_user: dict = Depends(get_current_user),
):
    """
    GET /suppliers/{supplier_id}
    Enforces that suppliers can only request their own details.
    """
    repo = SupplierRepository(db)
    if current_user["role"] == "supplier":
        resolved_id = _resolve_supplier_id(current_user, db)
        if supplier_id != resolved_id:
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
    if current_user["role"] == "supplier":
        resolved_id = _resolve_supplier_id(current_user, db)
        if supplier_id != resolved_id:
            raise HTTPException(status_code=403, detail="Not authorized to access these messages")

    supplier = SupplierRepository(db).get_by_supplier_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="supplier not found")

    return list(db["supplier_messages"].find({"supplier_id": supplier_id}, {"_id": 0}).sort("timestamp", 1))
