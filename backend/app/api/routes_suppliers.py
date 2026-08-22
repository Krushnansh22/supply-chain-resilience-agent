"""
app/api/routes_suppliers.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.common import SupplierOut

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

# TODO (Dev2): GET /suppliers/{supplier_id}/messages -- list supplier_messages for that supplier
