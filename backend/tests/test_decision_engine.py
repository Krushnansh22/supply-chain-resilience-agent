"""
tests/test_decision_engine.py
Owner: Developer 3 (Decision Engine)

Unit tests for pure business logic — no DB/LLM needed, so these should be fast and
runnable constantly during development (`pytest tests/test_decision_engine.py -v`).
"""

from app.decision_engine.inventory_calc import compute_days_of_supply, is_below_safety_stock
from app.decision_engine.constraint_validator import check_budget, check_moq


def test_compute_days_of_supply_basic():
    assert compute_days_of_supply(390, 90) == 4.33


def test_compute_days_of_supply_zero_usage():
    assert compute_days_of_supply(390, 0) == float("inf")


def test_is_below_safety_stock():
    assert is_below_safety_stock(50, 100) is True
    assert is_below_safety_stock(150, 100) is False


def test_check_budget_pass():
    result = check_budget(total_cost=40000, max_budget=50000)
    assert result.passed is True


def test_check_budget_fail():
    result = check_budget(total_cost=60000, max_budget=50000)
    assert result.passed is False


def test_check_moq_fail():
    result = check_moq(quantity=50, moq=100)
    assert result.passed is False

# TODO (Dev3): add tests for supplier_scoring.score_supplier and
# recovery_planner.build_recovery_plan once implemented, including a split-sourcing case.
