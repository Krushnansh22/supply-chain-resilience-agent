"""
app/api/routes_inventory.py
Owner: Developer 2 (Backend / Simulation)

REST surface for the `inventory` table. See docs/API_CONTRACTS.md for exact routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator, Field

from app.database import get_db
from app.models.inventory import Inventory
from app.schemas.common import InventoryOut
from app.decision_engine.inventory_calc import compute_days_of_supply
from app.middleware.security import require_api_key
from app.middleware.rate_limiter import check_rate_limit

router = APIRouter()

# Only alphanumerics and hyphens — blocks path traversal, null bytes, SQL injection.
_ID_PATTERN = r"^[A-Za-z0-9_-]+$"


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
def get_component(
    component_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    db: Session = Depends(get_db),
):
    """GET /inventory/{component_id}"""
    row = db.query(Inventory).filter(Inventory.component_id == component_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="component not found")
    item = InventoryOut.model_validate(row)
    item.days_of_supply = compute_days_of_supply(row.usable_stock, row.daily_usage)
    return item


class AdjustRequest(BaseModel):
    delta: int = Field(..., ge=-100_000, le=100_000, description="Stock delta — positive to add, negative to reduce")
    reason: str = Field(..., min_length=3, max_length=256, description="Human-readable reason for audit trail")

    @field_validator("reason")
    @classmethod
    def sanitize_reason(cls, v: str) -> str:
        # Strip leading/trailing whitespace and null bytes
        v = v.strip().replace("\x00", "")
        if not v:
            raise ValueError("reason must not be blank")
        return v

    class Config:
        extra = "forbid"


@router.post("/{component_id}/adjust", response_model=InventoryOut)
def adjust_inventory(
    request: Request,
    component_id: str = Path(..., pattern=_ID_PATTERN, min_length=1, max_length=32),
    req: AdjustRequest = ...,
    db: Session = Depends(get_db),
    _auth: None = Depends(require_api_key),
):
    """
    POST /inventory/{component_id}/adjust
    Adjusts usable_stock by delta. Rate limited: 30/min per IP.
    """
    check_rate_limit(request, bucket="inventory_adjust", max_calls=30, window_seconds=60)

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
