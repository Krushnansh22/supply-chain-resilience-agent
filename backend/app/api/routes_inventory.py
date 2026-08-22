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

# TODO (Dev2): POST /inventory/{component_id}/adjust  -- used by update_erp tool
