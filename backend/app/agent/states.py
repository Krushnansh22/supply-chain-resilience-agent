"""
app/agent/states.py
Owner: Developer 1 (Agent)

REQUIRED shape (team doc Section 20 lists these states explicitly):
    DETECTED -> INVESTIGATING -> SUPPLIER_CONTACT -> EVALUATING -> PLAN_READY
    -> WAITING_APPROVAL -> EXECUTING -> RESOLVED
    (any state) -> REPLANNING -> back into EVALUATING/PLAN_READY

RECEIVES: nothing (pure enum/constants module)
DELIVERS: imported by agent_loop.py to drive the state machine, and mirrored in
          Incident.status (app/models/incidents.py) so the frontend can show it.
See docs/AGENT_STATE_MACHINE.md for the full transition diagram.
"""

from enum import StrEnum


class AgentState(StrEnum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    SUPPLIER_CONTACT = "SUPPLIER_CONTACT"
    EVALUATING = "EVALUATING"
    PLAN_READY = "PLAN_READY"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    RESOLVED = "RESOLVED"
    REPLANNING = "REPLANNING"
