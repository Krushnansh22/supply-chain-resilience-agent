"""
backend/tests/test_rbac.py
Tests Role-Based Access Control (RBAC) and Multi-Warehouse Data Isolation:
- ADMIN global access and warehouse scope switching
- WAREHOUSE_MANAGER strict scoping to assigned warehouse
- Cross-warehouse mutation block (403 Forbidden)
- User and warehouse registry endpoints
"""

import pytest
import mongomock
from starlette.requests import Request
from fastapi import HTTPException

from app.middleware.rbac import get_current_user_and_scope, require_admin
from app.api.routes_inventory import list_inventory, adjust_inventory, AdjustRequest
from app.api.routes_users import get_current_user_profile, list_users, list_warehouses


@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client["scda_test_db"]

    # Seed users
    db["users"].insert_many([
        {
            "user_id": "USR-ADMIN",
            "name": "Alex Whitfield",
            "email": "alex.whitfield@atlas-scm.io",
            "role": "ADMIN",
            "assigned_warehouse": "ALL",
        },
        {
            "user_id": "USR-MGR-A",
            "name": "Marcus Vance",
            "email": "marcus.vance@atlas-scm.io",
            "role": "WAREHOUSE_MANAGER",
            "assigned_warehouse": "Warehouse-A",
        },
        {
            "user_id": "USR-MGR-B",
            "name": "Elena Rostova",
            "email": "elena.rostova@atlas-scm.io",
            "role": "WAREHOUSE_MANAGER",
            "assigned_warehouse": "Warehouse-B",
        },
    ])

    # Seed warehouses
    db["warehouses"].insert_many([
        {"warehouse_id": "Warehouse-A", "name": "Warehouse-A (Main Assembly)", "region": "North America"},
        {"warehouse_id": "Warehouse-B", "name": "Warehouse-B (Sub-Assembly Depot)", "region": "Central Hub"},
    ])

    # Seed inventory across warehouses
    db["inventory"].insert_many([
        {"component_id": "COMP-101", "name": "Resistor 10k", "usable_stock": 2400, "current_stock": 2400, "safety_stock": 360, "daily_usage": 120.0, "location": "Warehouse-A"},
        {"component_id": "COMP-104", "name": "Voltage Regulator VR-5A", "usable_stock": 390, "current_stock": 390, "safety_stock": 100, "daily_usage": 90.0, "location": "Warehouse-A"},
        {"component_id": "COMP-103", "name": "Microcontroller MCU-32X", "usable_stock": 80, "current_stock": 80, "safety_stock": 150, "daily_usage": 50.0, "location": "Warehouse-B"},
        {"component_id": "COMP-105", "name": "Inductor 47uH", "usable_stock": 3000, "current_stock": 3000, "safety_stock": 150, "daily_usage": 50.0, "location": "Warehouse-C"},
    ])

    return db


def test_admin_global_and_scoped_access(mock_db):
    # 1. Admin without warehouse filter -> sees ALL
    scope_global = Request({
        "type": "http",
        "headers": [(b"x-user-id", b"USR-ADMIN")],
        "query_string": b"",
    })
    ctx_global = get_current_user_and_scope(scope_global, mock_db)
    assert ctx_global["role"] == "ADMIN"
    assert ctx_global["effective_warehouse"] is None

    inv_global = list_inventory(db=mock_db, context=ctx_global)
    assert len(inv_global) == 4

    # 2. Admin filters to Warehouse-A
    scope_wh_a = Request({
        "type": "http",
        "headers": [(b"x-user-id", b"USR-ADMIN"), (b"x-warehouse-id", b"Warehouse-A")],
        "query_string": b"",
    })
    ctx_wh_a = get_current_user_and_scope(scope_wh_a, mock_db)
    assert ctx_wh_a["effective_warehouse"] == "Warehouse-A"

    inv_wh_a = list_inventory(db=mock_db, context=ctx_wh_a)
    assert len(inv_wh_a) == 2
    assert all(i.location == "Warehouse-A" for i in inv_wh_a)


def test_warehouse_manager_strict_isolation(mock_db):
    # Manager A is strictly locked to Warehouse-A
    scope_mgr_a = Request({
        "type": "http",
        "headers": [(b"x-user-id", b"USR-MGR-A")],
        "query_string": b"",
    })
    ctx_mgr_a = get_current_user_and_scope(scope_mgr_a, mock_db)
    assert ctx_mgr_a["role"] == "WAREHOUSE_MANAGER"
    assert ctx_mgr_a["effective_warehouse"] == "Warehouse-A"

    inv_mgr_a = list_inventory(db=mock_db, context=ctx_mgr_a)
    assert len(inv_mgr_a) == 2
    assert {i.component_id for i in inv_mgr_a} == {"COMP-101", "COMP-104"}


def test_warehouse_manager_cross_warehouse_tampering_blocked(mock_db):
    # 1. Attempting to query Warehouse-B header with Manager A credentials raises 403 Forbidden
    scope_tamper = Request({
        "type": "http",
        "headers": [(b"x-user-id", b"USR-MGR-A"), (b"x-warehouse-id", b"Warehouse-B")],
        "query_string": b"",
    })
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_and_scope(scope_tamper, mock_db)
    assert exc_info.value.status_code == 403

    # 2. Attempting to adjust stock in Warehouse-B with Manager A context raises 403 Forbidden
    ctx_mgr_a = {
        "role": "WAREHOUSE_MANAGER",
        "effective_warehouse": "Warehouse-A",
        "assigned_warehouse": "Warehouse-A",
    }
    req_dummy = Request({"type": "http", "client": ("127.0.0.1", 12345), "headers": []})
    adj = AdjustRequest(delta=10, reason="Unauthorized restock attempt")

    with pytest.raises(HTTPException) as exc_info_adj:
        adjust_inventory(
            request=req_dummy,
            component_id="COMP-103",  # Located in Warehouse-B
            req=adj,
            db=mock_db,
            _auth=None,
            context=ctx_mgr_a,
        )
    assert exc_info_adj.value.status_code == 403
    assert "cannot adjust inventory" in exc_info_adj.value.detail


def test_users_and_warehouses_api_endpoints(mock_db):
    users = list_users(db=mock_db)
    assert len(users) == 3
    assert {u["user_id"] for u in users} == {"USR-ADMIN", "USR-MGR-A", "USR-MGR-B"}

    whs = list_warehouses(db=mock_db)
    assert len(whs) == 2
    assert {w["warehouse_id"] for w in whs} == {"Warehouse-A", "Warehouse-B"}
