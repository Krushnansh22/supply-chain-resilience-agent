"""
tests/test_tools.py
Owner: Developer 2 (Backend / Simulation)

Automated tests for tools in app/tools/*.py using in-memory MongoDB (mongomock).
"""

import mongomock
import pytest

from app.tools.inventory_tools import get_inventory, adjust_inventory
from app.tools.rfq_tools import request_rfq


@pytest.fixture
def mock_db():
    return mongomock.MongoClient()["test_tools_db"]


def test_get_inventory_returns_days_of_supply(mock_db):
    """get_inventory tool returns correct stock and computed days of supply."""
    mock_db["inventory"].insert_one({
        "component_id": "COMP-001",
        "usable_stock": 500,
        "daily_usage": 50.0,
        "safety_stock": 100,
        "current_stock": 550,
    })

    result = get_inventory("COMP-001", mock_db)
    assert result.success is True
    assert result.data["component_id"] == "COMP-001"
    assert result.data["usable_stock"] == 500
    assert result.data["days_of_supply"] == 10.0
    assert "Checked inventory" in result.summary


def test_get_inventory_not_found(mock_db):
    """get_inventory returns failure when component does not exist."""
    result = get_inventory("COMP-NOT-FOUND", mock_db)
    assert result.success is False
    assert "not found" in result.error.lower()


def test_adjust_inventory_updates_stock(mock_db):
    """adjust_inventory increases usable stock and updates days of supply."""
    mock_db["inventory"].insert_one({
        "component_id": "COMP-001",
        "usable_stock": 100,
        "daily_usage": 10.0,
        "safety_stock": 20,
    })

    result = adjust_inventory("COMP-001", 50, mock_db)
    assert result.success is True
    assert result.data["usable_stock"] == 150
    assert result.data["days_of_supply"] == 15.0


def test_request_rfq_persists_rows(mock_db):
    """request_rfq simulates quotes and persists records to the rfqs collection."""
    supplier_ids = ["SUP-001", "SUP-002"]
    result = request_rfq("COMP-001", 200, supplier_ids, mock_db)

    assert result.success is True
    assert len(result.data) == 2
    assert mock_db["rfqs"].count_documents({"component_id": "COMP-001"}) == 2


def test_get_production_orders_evaluates_risk_without_attribute_error(mock_db):
    """get_production_orders correctly accesses dictionary items without AttributeError."""
    from datetime import datetime, timezone, timedelta
    from app.tools.production_tools import get_production_orders

    mock_db["inventory"].insert_one({
        "component_id": "COMP-104",
        "usable_stock": 100,
        "daily_usage": 50.0,
    })
    mock_db["production_orders"].insert_one({
        "production_id": "PROD-999",
        "product": "Industrial Controller",
        "component_id": "COMP-104",
        "quantity": 100,
        "priority": "HIGH",
        "deadline": datetime.now(timezone.utc) + timedelta(days=10),
    })

    result = get_production_orders("COMP-104", mock_db)
    assert result.success is True
    assert len(result.data) == 1
    assert result.data[0]["production_id"] == "PROD-999"
    assert result.data[0]["risk_level"] in ("CRITICAL", "HIGH")


def test_update_erp_executes_recovery_option(mock_db):
    """update_erp creates POs, increments stock, and resolves incident."""
    from app.tools.erp_tools import update_erp
    from app.schemas.recovery_plan import RecoveryPlanOption, SupplierAllocation

    mock_db["incidents"].insert_one({
        "incident_id": "INC-ERP-01",
        "affected_component": "COMP-104",
        "status": "EXECUTING",
    })
    mock_db["inventory"].insert_one({
        "component_id": "COMP-104",
        "usable_stock": 100,
        "daily_usage": 10.0,
    })

    option = RecoveryPlanOption(
        option_id="A",
        allocations=[
            SupplierAllocation(
                supplier_id="SUP-001",
                quantity=500,
                unit_price=10.0,
                delivery_days=3,
            )
        ],
        total_cost=5000.0,
        max_delivery_days=3,
        constraints_satisfied=True,
    )

    res = update_erp("INC-ERP-01", option, mock_db)
    assert res.success is True
    assert len(res.data["purchase_orders_created"]) == 1

    # Check incident was resolved
    inc = mock_db["incidents"].find_one({"incident_id": "INC-ERP-01"})
    assert inc["status"] == "RESOLVED"

    # Check usable stock increased
    inv = mock_db["inventory"].find_one({"component_id": "COMP-104"})
    assert inv["usable_stock"] == 600


def test_update_erp_rejects_missing_incident(mock_db):
    """update_erp returns failure when incident does not exist."""
    from app.tools.erp_tools import update_erp
    from app.schemas.recovery_plan import RecoveryPlanOption, SupplierAllocation

    option = RecoveryPlanOption(
        option_id="A",
        allocations=[
            SupplierAllocation(
                supplier_id="SUP-001",
                quantity=100,
                unit_price=5.0,
                delivery_days=2,
            )
        ],
        total_cost=500.0,
        max_delivery_days=2,
        constraints_satisfied=True,
    )

    res = update_erp("INC-GHOST-999", option, mock_db)
    assert res.success is False
    assert "not found" in res.error.lower()
