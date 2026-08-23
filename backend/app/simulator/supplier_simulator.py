"""
app/simulator/supplier_simulator.py
Owner: Developer 2 (Backend / Simulation)

Simulates supplier communications, carrier tracking, and dynamic negotiation behaviors.
Supports:
- Contradictory statements (claims dispatch while carrier has no scan)
- Vague/ambiguous initial responses requiring agent challenge
- Partial fulfillment and split-order availability
- Expedite fee and commercial concessions upon pushback
- Deterministic and reproducible synthetic RFQs
"""

import random
from typing import Optional

# In-memory registry: active lie POs, negotiation turns, and conceded POs
_active_lie_pos: set[str] = set()
_conceded_pos: set[str] = set()
_conversation_history: dict[str, list[dict]] = {}


def register_supplier_lie(po_id: str) -> None:
    """Called when a SUPPLIER_LIE incident is created."""
    _active_lie_pos.add(po_id)
    _conceded_pos.discard(po_id)


def reset_simulator_state() -> None:
    """Reset all active simulator state (useful for tests)."""
    _active_lie_pos.clear()
    _conceded_pos.clear()
    _conversation_history.clear()


def simulate_supplier_reply(
    supplier_id: str,
    po_id: str,
    outbound_message: str,
    component_id: Optional[str] = None,
) -> str:
    """
    Returns a realistic, dynamic simulated supplier reply.
    Responds to pushback, challenges, and specific questions from the agent.
    """
    msg_lower = outbound_message.lower()
    key = f"{supplier_id}:{po_id}"
    history = _conversation_history.setdefault(key, [])
    history.append({"role": "agent", "content": outbound_message})

    # Case 1: Supplier Lie Scenario
    if po_id in _active_lie_pos:
        # If agent challenges the dispatch claim or mentions tracking / contradiction / no pickup
        if any(term in msg_lower for term in ["tracking", "pickup", "contradiction", "verify", "falsifiable", "carrier", "no scan", "challenge", "clarify", "evidence"]):
            _conceded_pos.add(po_id)
            reply = (
                f"We acknowledge the discrepancy. The carrier label was generated yesterday but physical pickup was delayed due to packaging line downtime. "
                f"Goods will physically depart our warehouse in 24 hours. We can absorb a 50% discount on expedited air transit (${supplier_id}-EXP) to maintain delivery."
            )
        elif po_id in _conceded_pos:
            reply = "Confirmed: expedited logistics have been booked. Pickup scheduled for 14:00 today. Tracking will show movement within 4 hours."
        else:
            # First turn in lie scenario: falsely claim dispatch
            reply = (
                "We confirm the shipment has been dispatched as of yesterday morning. "
                "Tracking number has been assigned and carrier transit is underway."
            )
        history.append({"role": "supplier", "content": reply})
        return reply

    # Case 2: Agent is pushing back on a vague claim or asking for exact date/falsifiable commitment
    if any(term in msg_lower for term in ["exact date", "firm date", "commit", "falsifiable", "guarantee", "specific", "clarify", "how many units", "partial"]):
        reply = (
            f"FIRM COMMITMENT: We can guarantee dispatch of 600 units within 3 days, and the remaining balance within 7 days. "
            f"Expedited dispatch is available immediately for an additional $1,200 courier fee."
        )
        history.append({"role": "supplier", "content": reply})
        return reply

    # Case 3: Inquire about expedite fees or rush options
    if any(term in msg_lower for term in ["expedite", "rush", "fee", "air freight", "fast"]):
        reply = (
            f"We can expedite manufacturing and shift to dedicated air freight. "
            f"This reduces lead time to 2 business days for an expedite surcharge of $1,800."
        )
        history.append({"role": "supplier", "content": reply})
        return reply

    # Case 4: Default conversational response (some realistic ambiguity)
    turn_count = len([m for m in history if m["role"] == "agent"])
    if turn_count <= 1:
        canned_replies = [
            "We are currently facing a 4-6 day production delay due to raw material sequencing. We are assessing recovery options.",
            "Our line is operating at 80% capacity. We anticipate a minor delay of 5 to 7 days.",
            "Shipment is being processed in our warehouse. Expedited courier service can be arranged upon request.",
            "We can fulfill approximately 50% of the purchase order by the original target date, with the remainder following shortly.",
        ]
        seed = sum(ord(c) for c in (supplier_id + po_id))
        reply = canned_replies[seed % len(canned_replies)]
    else:
        reply = (
            f"Updated status from dispatch manager: We confirm a revised delivery window of 4 business days. "
            f"Quality control checks for component batch have been completed."
        )

    history.append({"role": "supplier", "content": reply})
    return reply


def simulate_tracking_status(po_id: str) -> str:
    """
    Returns simulated carrier tracking status.
    For active supplier-lie POs that haven't been conceded yet: returns NO_PICKUP_SCAN.
    After concession or normal POs: returns IN_TRANSIT or LABEL_CREATED.
    """
    if po_id in _active_lie_pos and po_id not in _conceded_pos:
        return "NO_PICKUP_SCAN"
    elif po_id in _conceded_pos:
        return "LABEL_CREATED"

    return "IN_TRANSIT"


def simulate_rfq_response(supplier_id: str, component_id: str, quantity: int) -> dict:
    """
    Returns a synthetic RFQ quote. Deterministic based on supplier_id and component_id.
    """
    seed = sum(ord(c) for c in supplier_id) + sum(ord(c) for c in component_id)
    rng = random.Random(seed + quantity)

    # Base pricing and lead times calibrated across suppliers
    base_price = 120.0 + (seed % 45)
    delivery_days = 2 + (seed % 7)
    expedite_available = (seed % 2 == 0)
    expedite_fee = round(rng.uniform(500, 2500), 2) if expedite_available else 0.0
    moq = 50 if (seed % 3 == 0) else 0

    return {
        "unit_price": round(base_price, 2),
        "delivery_days": delivery_days,
        "expedite_available": expedite_available,
        "expedite_fee": expedite_fee,
        "moq": moq,
        "available_quantity": max(quantity, int(quantity * rng.uniform(0.8, 1.5))),
    }
