# Agent State Machine

Owner: Developer 1 (Agent). States are defined in `backend/app/agent/states.py`
(`AgentState` enum) and mirrored into `Incident.status` on every transition so the
frontend can show progress without a separate polling endpoint.

**REQUIRED shape** — sourced directly from team doc Section 20's stated states; the
exact transition logic beyond that is a **CHOSEN** implementation detail for Dev1.

```
DETECTED
   |
   v
INVESTIGATING  ------------------------------+
   |  (get_inventory, get_production_orders) |
   v                                         |
SUPPLIER_CONTACT                             |
   |  (send_supplier_message,                |
   |   get_tracking_status)                  |
   v                                         |
EVALUATING  <---------------------------+    |
   |  (request_rfq, build_recovery_plan)|    |
   v                                    |    |
PLAN_READY                              |    |
   |  (check_approval)                  |    |
   +--> cost <= limit --> EXECUTING     |    |
   |         |                          |    |
   |         v                          |    |
   |     RESOLVED  (update_erp)         |    |
   |                                    |    |
   +--> cost > limit --> WAITING_APPROVAL     |
                 |         |                  |
          human REJECT   human APPROVE        |
                 |         |                  |
                 v         v                  |
            REPLANNING -> EXECUTING -> RESOLVED

Any state (esp. PLAN_READY / WAITING_APPROVAL / EXECUTING) can be interrupted by a
NEW incident affecting the same component/supplier. When
decision_engine/replanning.is_plan_invalidated() returns True:
   current state --> REPLANNING --> back to EVALUATING with updated context
```

## Notes for implementation (`agent_loop.py`)
- `INVESTIGATING`: agent must call `get_inventory` and `get_production_orders` before
  moving on — this is what produces the "Checked inventory / Checked production" audit
  lines judges expect (docs Section 13/14 of team doc).
- `SUPPLIER_CONTACT`: agent should call `get_tracking_status` whenever the supplier
  claims dispatch, to support the SUPPLIER_LIE contradiction-detection scenario.
- `EVALUATING`: may loop multiple times (more RFQs, re-scoring) before `PLAN_READY`.
- `WAITING_APPROVAL`: agent loop **must stop and return** here — do not proceed to
  `update_erp` until `/agent/approve` is called externally by a human.
- `REPLANNING`: always log a `decision="REPLAN"` audit entry with `reason` explaining
  which incident/supplier invalidated the prior plan (team doc Section 19E demo beat).
