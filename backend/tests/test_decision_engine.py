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


def test_assess_production_risk_tz_aware_and_naive():
    from datetime import datetime, timezone, timedelta
    from app.decision_engine.production_risk import assess_production_risk

    deadline_aware = datetime.now(timezone.utc) + timedelta(days=10)
    # Should calculate without TypeError between aware deadline and default now
    res = assess_production_risk("PROD-1", days_of_supply=4.0, deadline=deadline_aware, priority="HIGH")
    assert res.risk_level == "CRITICAL"
    assert res.required_lead_time_days >= 9

    deadline_naive = datetime.now() + timedelta(days=10)
    res2 = assess_production_risk("PROD-2", days_of_supply=15.0, deadline=deadline_naive, priority="LOW")
    assert res2.risk_level == "LOW"


def test_score_supplier_auto_normalizes_scales():
    from app.decision_engine.supplier_scoring import score_supplier

    # Test 0-1 normalized scale (0.95, 0.90)
    res_normalized = score_supplier(
        supplier_id="SUP-1",
        quality_score=0.95,
        reliability_score=0.90,
        delivery_days=3,
        unit_price=10.0,
        max_acceptable_delivery_days=10,
        max_acceptable_price=50.0,
    )

    # Test 0-100 scale (95, 90)
    res_100 = score_supplier(
        supplier_id="SUP-1",
        quality_score=95.0,
        reliability_score=90.0,
        delivery_days=3,
        unit_price=10.0,
        max_acceptable_delivery_days=10,
        max_acceptable_price=50.0,
    )

    assert res_normalized.score == res_100.score
    assert res_normalized.score > 0.7


def test_triage_incident_normalized_scores_not_falsely_flagged_as_critical_risk():
    from app.decision_engine.severity_triage import triage_incident, TriageInput

    # High quality supplier on 0-1 scale (0.95 quality)
    inp = TriageInput(
        incident_type="STALE_INVENTORY",
        usable_stock=1000,
        daily_usage=10.0,
        safety_stock=100,
        supplier_quality_score=0.95,
        supplier_reliability_score=0.95,
    )
    res = triage_incident(inp)
    # Factor supplier_risk must be 0.0 because 95% is high quality
    assert res.factors["supplier_risk"] == 0.0
    assert res.severity == "LOW"
