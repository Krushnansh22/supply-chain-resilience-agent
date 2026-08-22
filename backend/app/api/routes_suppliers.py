"""
app/api/routes_suppliers.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.suppliers import Supplier
from app.schemas.common import SupplierOut

router = APIRouter()


@router.get("/", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    row = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="supplier not found")
    return row

# TODO (Dev2): GET /suppliers/{supplier_id}/messages -- list supplier_messages for that supplier
