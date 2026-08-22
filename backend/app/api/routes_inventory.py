"""
app/api/routes_inventory.py
Owner: Developer 2 (Backend / Simulation)

REST surface for the `inventory` table. See docs/API_CONTRACTS.md for exact routes.

RECEIVES: DB session via get_db()
DELIVERS: JSON consumed by (a) frontend Inventory page (Dev4) and
          (b) indirectly by tools/inventory_tools.py which the agent calls.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.inventory import Inventory
from app.schemas.common import InventoryOut
from app.decision_engine.inventory_calc import compute_days_of_supply

router = APIRouter()


@router.get("/", response_model=list[InventoryOut])
def list_inventory(db: Session = Depends(get_db)):
    """GET /inventory -> all components with computed days_of_supply."""
    rows = db.query(Inventory).all()
    out = []
    for r in rows:
        item = InventoryOut.model_validate(r)
        item.days_of_supply = compute_days_of_supply(r.usable_stock, r.daily_usage)
        out.append(item)
    return out


@router.get("/{component_id}", response_model=InventoryOut)
def get_component(component_id: str, db: Session = Depends(get_db)):
    """GET /inventory/{component_id}"""
    row = db.query(Inventory).filter(Inventory.component_id == component_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="component not found")
    item = InventoryOut.model_validate(row)
    item.days_of_supply = compute_days_of_supply(row.usable_stock, row.daily_usage)
    return item


class AdjustRequest(BaseModel):
    delta: int    # positive = add stock, negative = remove stock
    reason: str   # human-readable reason for audit trail


@router.post("/{component_id}/adjust", response_model=InventoryOut)
def adjust_inventory(component_id: str, req: AdjustRequest, db: Session = Depends(get_db)):
    """
    POST /inventory/{component_id}/adjust
    Adjusts usable_stock by delta (positive = add, negative = reduce).
    Used by update_erp tool and convenience endpoints.
    """
    row = db.query(Inventory).filter(Inventory.component_id == component_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="component not found")

    new_stock = row.usable_stock + req.delta
    if new_stock < 0:
        raise HTTPException(
            status_code=422,
            detail=f"Adjustment would result in negative stock ({new_stock}). Current usable: {row.usable_stock}.",
        )

    row.usable_stock = new_stock
    row.current_stock = max(row.current_stock + req.delta, row.usable_stock)
    db.commit()
    db.refresh(row)

    item = InventoryOut.model_validate(row)
    item.days_of_supply = compute_days_of_supply(row.usable_stock, row.daily_usage)
    return item
