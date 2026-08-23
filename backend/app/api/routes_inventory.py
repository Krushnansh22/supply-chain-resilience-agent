"""
app/api/routes_inventory.py
Owner: Developer 2 (Backend / Simulation)

REST surface for the `inventory` table. See docs/API_CONTRACTS.md for exact routes.
"""

import math
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from pymongo.database import Database
from pydantic import BaseModel, ConfigDict, field_validator, Field

from app.mongo_database import get_mongo_db
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.common import InventoryOut
from app.decision_engine.inventory_calc import compute_days_of_supply
from app.middleware.security import require_api_key
from app.middleware.rate_limiter import check_rate_limit

from app.middleware.rbac import get_current_user_and_scope
from typing import Dict, Any

router = APIRouter()

# Only alphanumerics and hyphens — blocks path traversal, null bytes, SQL injection.
_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


@router.get("/", response_model=list[InventoryOut])
def list_inventory(
    db: Database = Depends(get_mongo_db),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """GET /inventory -> all components with computed days_of_supply, filtered by effective warehouse."""
    repo = InventoryRepository(db)
    rows = repo.list_all()
    eff_warehouse = context.get("effective_warehouse")
    if eff_warehouse:
        rows = [r for r in rows if r.get("location") == eff_warehouse]
    out = []
    for r in rows:
        item = InventoryOut(**r)
        days_of_supply = compute_days_of_supply(r["usable_stock"], r["daily_usage"])
        item.days_of_supply = days_of_supply if math.isfinite(days_of_supply) else None
        out.append(item)
    return out


@router.get("/{component_id}", response_model=InventoryOut)
def get_component(
    component_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    db: Database = Depends(get_mongo_db),
):
    """GET /inventory/{component_id}"""
    repo = InventoryRepository(db)
    row = repo.get_by_component_id(component_id)
    if not row:
        raise HTTPException(status_code=404, detail="component not found")
    item = InventoryOut(**row)
    days_of_supply = compute_days_of_supply(row["usable_stock"], row["daily_usage"])
    item.days_of_supply = days_of_supply if math.isfinite(days_of_supply) else None
    return item


class AdjustRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delta: int = Field(..., ge=-100_000, le=100_000, description="Stock delta — positive to add, negative to reduce")
    reason: str = Field(..., min_length=3, max_length=256, description="Human-readable reason for audit trail")

    @field_validator("reason")
    @classmethod
    def sanitize_reason(cls, v: str) -> str:
        v = v.strip().replace("\x00", "")
        if not v:
            raise ValueError("reason must not be blank")
        return v


@router.post("/{component_id}/adjust", response_model=InventoryOut)
def adjust_inventory(
    request: Request,
    component_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    req: AdjustRequest = ...,
    db: Database = Depends(get_mongo_db),
    _auth: None = Depends(require_api_key),
    context: Dict[str, Any] = Depends(get_current_user_and_scope),
):
    """
    POST /inventory/{component_id}/adjust
    Adjusts usable_stock by delta. Rate limited: 30/min per IP.
    """
    check_rate_limit(request, bucket="inventory_adjust", max_calls=30, window_seconds=60)

    repo = InventoryRepository(db)
    row = repo.get_by_component_id(component_id)
    if not row:
        raise HTTPException(status_code=404, detail="component not found")

    eff_warehouse = context.get("effective_warehouse")
    if context.get("role") == "WAREHOUSE_MANAGER" and eff_warehouse and row.get("location") != eff_warehouse:
        raise HTTPException(
            status_code=403,
            detail=f"Forbidden: You are manager of '{eff_warehouse}' and cannot adjust inventory at '{row.get('location')}'."
        )

    new_stock = row["usable_stock"] + req.delta
    if new_stock < 0:
        raise HTTPException(
            status_code=422,
            detail=f"Adjustment would result in negative stock ({new_stock}). Current usable: {row['usable_stock']}.",
        )

    new_current = max(row["current_stock"] + req.delta, new_stock)
    db["inventory"].update_one(
        {"component_id": component_id},
        {"$set": {"usable_stock": new_stock, "current_stock": new_current}},
    )

    updated_row = repo.get_by_component_id(component_id)
    item = InventoryOut(**updated_row)
    days_of_supply = compute_days_of_supply(updated_row["usable_stock"], updated_row["daily_usage"])
    item.days_of_supply = days_of_supply if math.isfinite(days_of_supply) else None
    return item
