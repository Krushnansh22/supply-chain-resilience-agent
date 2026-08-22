"""
app/api/routes_suppliers.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.suppliers import Supplier
from app.models.supplier_messages import SupplierMessage
from app.schemas.common import SupplierOut, SupplierMessageOut

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


@router.get("/{supplier_id}/messages", response_model=List[SupplierMessageOut])
def get_supplier_messages(supplier_id: str, db: Session = Depends(get_db)):
    """
    GET /suppliers/{supplier_id}/messages
    Returns all messages exchanged with this supplier (both outbound and simulated inbound),
    ordered chronologically. Used by frontend supplier message thread display.
    """
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="supplier not found")

    messages = (
        db.query(SupplierMessage)
        .filter(SupplierMessage.supplier_id == supplier_id)
        .order_by(SupplierMessage.timestamp.asc())
        .all()
    )
    return messages
