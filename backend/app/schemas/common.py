"""
app/schemas/common.py
Owner: Shared — Developer 2 maintains, but ALL devs read this before changing shapes.

These are the Pydantic (request/response) models frontend (Dev4) and agent (Dev1) code
against. If you need a new field, add it here FIRST and announce it in the team channel
so nobody's local branch silently diverges. This file mirrors docs/API_CONTRACTS.md —
keep them in sync.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InventoryOut(BaseModel):
    component_id: str
    current_stock: int
    usable_stock: int
    daily_usage: float
    safety_stock: int
    days_of_supply: Optional[float] = None  # computed field, filled by decision_engine

    class Config:
        from_attributes = True


class SupplierOut(BaseModel):
    supplier_id: str
    name: str
    quality_score: float
    reliability_score: float
    certifications: Optional[str] = None

    class Config:
        from_attributes = True


class ProductionOrderOut(BaseModel):
    production_id: str
    product: str
    component_id: str
    quantity: int
    component_per_unit: int
    deadline: Optional[datetime] = None
    priority: str
    status: str

    class Config:
        from_attributes = True


class IncidentOut(BaseModel):
    incident_id: str
    type: str
    severity: str
    affected_component: Optional[str] = None
    affected_po: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    timestamp: datetime
    incident_id: Optional[str] = None
    action: str
    tool: Optional[str] = None
    result: Optional[str] = None
    decision: Optional[str] = None
    reason: Optional[str] = None

    class Config:
        from_attributes = True
