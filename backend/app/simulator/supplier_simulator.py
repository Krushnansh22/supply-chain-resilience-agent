"""
app/simulator/supplier_simulator.py
Owner: Developer 2 (Backend / Simulation)

Fakes supplier + carrier behavior so the agent has something realistic to call.
Also implements the "supplier lie" scenario: reply text claims dispatch while
tracking status says NO_PICKUP_SCAN (team doc Section 19B).

RECEIVES: calls from app/tools/supplier_tools.py and app/tools/rfq_tools.py
DELIVERS: dict payloads consumed directly by those tools (no DB writes here — the
          calling tool owns persistence).
"""

import random
from sqlalchemy.orm import Session

# In-memory registry: incident_id -> scenario type
# Set by disruption_injector when a scenario is injected.
# Keyed by (supplier_id, po_id) for supplier-lie detection.
_active_lie_pos: set[str] = set()


def register_supplier_lie(po_id: str) -> None:
    """Called by disruption_injector when a SUPPLIER_LIE incident is created."""
    _active_lie_pos.add(po_id)


def simulate_supplier_reply(supplier_id: str, po_id: str, outbound_message: str) -> str:
    """
    Returns a simulated supplier reply.
    For SUPPLIER_LIE scenario: always claims dispatch so the agent can detect the
    contradiction with simulate_tracking_status() returning NO_PICKUP_SCAN.
    """
    if po_id in _active_lie_pos:
        return (
            "We confirm the shipment has been dispatched as of yesterday. "
            "Tracking number will follow shortly."
        )

    canned_replies = [
        "We expect a 5-7 day delay due to a raw material shortage.",
        "Shipment has been dispatched and is on its way.",
        "We can expedite for an additional fee — please advise.",
        "Our production team is working overtime to meet the deadline.",
        "We have escalated this to our logistics partner for priority handling.",
    ]
    return random.choice(canned_replies)


def simulate_tracking_status(po_id: str) -> str:
    """
    Returns simulated carrier tracking status.
    For SUPPLIER_LIE scenario: deterministically returns NO_PICKUP_SCAN to
    contradict the supplier's claim of dispatch, enabling agent contradiction-detection.
    """
    if po_id in _active_lie_pos:
        return "NO_PICKUP_SCAN"

    return random.choice(["IN_TRANSIT", "IN_TRANSIT", "OUT_FOR_DELIVERY", "NO_PICKUP_SCAN"])


def simulate_rfq_response(supplier_id: str, component_id: str, quantity: int) -> dict:
    """
    Returns a synthetic RFQ quote. Varies slightly by supplier_id hash for
    reproducible variation (same supplier always quotes similar prices).
    """
    seed = sum(ord(c) for c in supplier_id)
    rng = random.Random(seed + quantity)
    return {
        "unit_price": round(rng.uniform(115, 165), 2),
        "delivery_days": rng.randint(2, 10),
        "expedite_available": rng.choice([True, False]),
        "expedite_fee": round(rng.uniform(400, 3500), 2),
    }
