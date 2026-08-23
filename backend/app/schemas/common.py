"""
app/schemas/common.py
Owner: Shared — Developer 2 maintains, but ALL devs read this before changing shapes.

These are the Pydantic (request/response) models frontend (Dev4) and agent (Dev1) code
against. If you need a new field, add it here FIRST and announce it in the team channel
so nobody's local branch silently diverges. This file mirrors docs/API_CONTRACTS.md —
keep them in sync.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    component_id: str
    name: Optional[str] = None
    current_stock: int
    usable_stock: Optional[int] = None
    daily_usage: float
    safety_stock: int
    location: Optional[str] = None
    days_of_supply: Optional[float] = None  # computed field, filled by decision_engine


class SupplierOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: str
    name: str
    quality_score: Optional[float] = None
    reliability_score: Optional[float] = None
    certifications: Optional[str] = None
    min_order_qty: Optional[int] = None


class ProductionOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    production_id: str
    product: str
    component_id: str
    quantity: int
    component_per_unit: int
    deadline: Optional[datetime] = None
    priority: str
    status: str
    plant_location: Optional[str] = None


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: str
    type: str
    severity: str
    affected_component: Optional[str] = None
    affected_po: Optional[str] = None
    status: str
    location: Optional[str] = None
    warehouse_id: Optional[str] = None
    resolution_mode: Optional[str] = None  # "AUTONOMOUS" | "HUMAN_APPROVED"
    resolved_by: Optional[str] = None
    autonomous_reasoning: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    incident_id: Optional[str] = None
    action: str
    tool: Optional[str] = None
    result: Optional[str] = None
    decision: Optional[str] = None
    reason: Optional[str] = None
    step_index: Optional[int] = None
    event_type: Optional[str] = None
    warehouse_id: Optional[str] = None


class SupplierMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: str
    supplier_id: str
    po_id: Optional[str] = None
    message: str
    timestamp: datetime
