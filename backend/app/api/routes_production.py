"""
app/api/routes_production.py
Owner: Developer 2 (Backend / Simulation)
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from pymongo.database import Database

from app.mongo_database import get_mongo_db
from app.repositories.production_order_repository import ProductionOrderRepository
from app.schemas.common import ProductionOrderOut

router = APIRouter()

_PRODUCTION_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


from app.middleware.rbac import get_current_user_and_scope
from typing import Dict, Any


def get_repo(db: Database = Depends(get_mongo_db)):
    return ProductionOrderRepository(db)


@router.get("/", response_model=list[ProductionOrderOut])
def list_production_orders(
    repo: ProductionOrderRepository = Depends(get_repo),
    db: Database = Depends(get_mongo_db),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    rows = repo.list_all()
    eff_warehouse = context.get("effective_warehouse")
    if eff_warehouse:
        comp_ids = {c["component_id"] for c in db["inventory"].find({"location": eff_warehouse}, {"component_id": 1})}
        rows = [r for r in rows if r.get("component_id") in comp_ids or r.get("plant_location") == eff_warehouse]
    return rows


@router.get("/{production_id}", response_model=ProductionOrderOut)
def get_production_order(
    production_id: str = Path(..., pattern=_PRODUCTION_ID_PATTERN, min_length=1, max_length=32),
    repo: ProductionOrderRepository = Depends(get_repo),
):
    row = repo.get_by_production_id(production_id)
    if not row:
        raise HTTPException(status_code=404, detail="production order not found")
    return row

# TODO (Dev3): expose a /production/{id}/risk endpoint wrapping decision_engine/production_risk.py
