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
