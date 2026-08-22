# Demo Script

Owner: whole team, rehearsed at Hour 16 (team doc Section 21). Mirrors team doc
Section 23 exactly — do not improvise new steps on stage.

1. **Show normal factory state** — Overview dashboard, zero/low active incidents.
2. **Click "Inject Supplier Delay"** (Simulator panel) — hero scenario: `PO-7712`,
   component `COMP-104`, supplier `SUP-21`.
3. **Critical incident appears** on Overview and in the Incident Command Center.
4. **Agent automatically:**
   - checks inventory (`get_inventory`)
   - checks production (`get_production_orders`)
   - checks supplier (`get_supplier`)
   - contacts supplier (`send_supplier_message`)
   - verifies tracking (`get_tracking_status`)
   - requests RFQs (`request_rfq`)
   - compares alternatives, rejects invalid supplier (constraint failure shown)
   - generates recovery plan (`build_recovery_plan`)
5. **If cost/risk requires approval** → Human Approval screen appears automatically.
6. **Judge clicks APPROVE.**
7. **Agent executes** (`update_erp`).
8. **ERP updates** — reflected in Inventory/Suppliers pages.
9. **Production becomes protected** — incident status moves toward RESOLVED.
10. **Inject another disruption** affecting the same supplier/component.
11. **Existing recovery plan becomes invalid.**
12. **Agent detects and announces:** "Recovery plan invalidated. Replanning…"
13. **Agent generates Plan B** and repeats the approval/execution flow.

## What to narrate while it runs
- Point at the Agent Activity feed, not the code — the audit log narration IS the
  explainability story the PS scores on.
- Explicitly say out loud: "the agent is choosing which tool to call based on what it
  just learned" at least once during step 4, to land the "not a hardcoded workflow"
  point from team doc Section 2.
- When the approval screen appears, say the exact number and the exact threshold
  ($50,000) so judges hear the PS requirement being enforced verbatim.

## Fallback plan if something breaks live
- Keep a screen-recorded backup of one full successful run (record during Hour 15
  stress testing) and be ready to switch to it without breaking narration.
- Keep the SQLite DB file from a known-good seed state as a quick `docker compose
  restart backend` reset between rehearsal attempts.
