"""
app/api/routes_production.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.production_orders import ProductionOrder
from app.schemas.common import ProductionOrderOut

router = APIRouter()

_PRODUCTION_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


@router.get("/", response_model=list[ProductionOrderOut])
def list_production_orders(db: Session = Depends(get_db)):
    return db.query(ProductionOrder).all()


@router.get("/{production_id}", response_model=ProductionOrderOut)
def get_production_order(
    production_id: str = Path(..., pattern=_PRODUCTION_ID_PATTERN, min_length=1, max_length=32),
    db: Session = Depends(get_db),
):
    row = db.query(ProductionOrder).filter(ProductionOrder.production_id == production_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="production order not found")
    return row

# TODO (Dev3): expose a /production/{id}/risk endpoint wrapping decision_engine/production_risk.py
