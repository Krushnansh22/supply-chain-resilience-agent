"""
app/api/routes_suppliers.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.common import SupplierOut
from app.schemas.common import SupplierMessageOut

router = APIRouter()

def get_repo(db: Database = Depends(get_mongo_db)):
    return SupplierRepository(db)


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(repo: SupplierRepository = Depends(get_repo)):
    return repo.list_all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: str, repo: SupplierRepository = Depends(get_repo)):
    row = repo.get_by_supplier_id(supplier_id)
    if not row:
        raise HTTPException(status_code=404, detail="supplier not found")
    return row


@router.get("/{supplier_id}/messages", response_model=List[SupplierMessageOut])
def get_supplier_messages(supplier_id: str, db: Database = Depends(get_mongo_db)):
    """
    GET /suppliers/{supplier_id}/messages
    Returns all messages exchanged with this supplier (both outbound and simulated inbound),
    ordered chronologically. Used by frontend supplier message thread display.
    """
    supplier = SupplierRepository(db).get_by_supplier_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="supplier not found")

    return list(db["supplier_messages"].find({"supplier_id": supplier_id}, {"_id": 0}).sort("timestamp", 1))
