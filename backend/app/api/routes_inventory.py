"""
app/api/routes_inventory.py
Owner: Developer 2 (Backend / Simulation)

REST surface for the `inventory` table. See docs/API_CONTRACTS.md for exact routes.

RECEIVES: DB session via get_db()
DELIVERS: JSON consumed by (a) frontend Inventory page (Dev4) and
          (b) indirectly by tools/inventory_tools.py which the agent calls.
"""

from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database
import math

from app.mongo_database import get_mongo_db
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.common import InventoryOut
from app.decision_engine.inventory_calc import compute_days_of_supply

router = APIRouter()


@router.get("/", response_model=list[InventoryOut])
def list_inventory(db: Database = Depends(get_mongo_db)):
    """GET /inventory -> all components with computed days_of_supply."""
    repo = InventoryRepository(db)
    rows = repo.list_all()
    out = []
    for r in rows:
        item = InventoryOut(**r)
        days_of_supply = compute_days_of_supply(r["usable_stock"], r["daily_usage"])
        item.days_of_supply = days_of_supply if math.isfinite(days_of_supply) else None
        out.append(item)
    return out


@router.get("/{component_id}", response_model=InventoryOut)
def get_component(component_id: str, db: Database = Depends(get_mongo_db)):
    """GET /inventory/{component_id}"""
    repo = InventoryRepository(db)
    row = repo.get_by_component_id(component_id)
    if not row:
        raise HTTPException(status_code=404, detail="component not found")
    item = InventoryOut(**row)
    days_of_supply = compute_days_of_supply(row["usable_stock"], row["daily_usage"])
    item.days_of_supply = days_of_supply if math.isfinite(days_of_supply) else None
    return item

# TODO (Dev2): POST /inventory/{component_id}/adjust  -- used by update_erp tool
