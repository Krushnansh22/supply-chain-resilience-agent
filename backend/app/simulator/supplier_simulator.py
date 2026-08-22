"""
app/simulator/supplier_simulator.py
Owner: Developer 2 (Backend / Simulation)

Fakes supplier + carrier behavior so the agent has something realistic to call.
Also implements the "supplier lie" scenario: reply text claims dispatch while
tracking status says no pickup scan (team doc Section 19B).

RECEIVES: calls from app/tools/supplier_tools.py and app/tools/rfq_tools.py
DELIVERS: dict payloads consumed directly by those tools (no DB writes here — the
          calling tool owns persistence).
"""

import random


def simulate_supplier_reply(supplier_id: str, po_id: str, outbound_message: str) -> str:
    """
    TODO (Dev2/Dev3): wire this to the active disruption scenario (e.g. if the
    triggering incident type is SUPPLIER_LIE, always return a dispatch claim here so
    it can be contradicted by simulate_tracking_status()). For now, canned replies:
    """
    canned_replies = [
        "We expect a 5-7 day delay due to a raw material shortage.",
        "Shipment has been dispatched and is on its way.",
        "We can expedite for an additional fee — please advise.",
    ]
    return random.choice(canned_replies)


def simulate_tracking_status(po_id: str) -> str:
    """
    TODO (Dev2/Dev3): for the SUPPLIER_LIE demo scenario this should deterministically
    return "NO_PICKUP_SCAN" for the PO tied to that incident, so the agent's
    contradiction-detection (decision_engine) can flag it.
    """
    return random.choice(["IN_TRANSIT", "NO_PICKUP_SCAN", "OUT_FOR_DELIVERY"])


def simulate_rfq_response(supplier_id: str, component_id: str, quantity: int) -> dict:
    """Returns a synthetic quote. TODO (Dev2/Dev3): vary by supplier profile/scenario."""
    return {
        "unit_price": round(random.uniform(120, 160), 2),
        "delivery_days": random.randint(2, 9),
        "expedite_available": random.choice([True, False]),
        "expedite_fee": round(random.uniform(500, 3000), 2),
    }
