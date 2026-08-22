# Feature Checklist

Legend: **[R]** Required by official PS · **[REC]** Recommended (implied by PS/scoring)
· **[C]** Chosen (our design decision) · **[O]** Optional / cut first under time pressure

Copy this file's checkboxes into your team's tracker (Notion/GitHub Projects/etc.) at
Hour 0. Update status live during integration checkpoints (Hours 3/6/10/13/16).

---

## Foundation (Hour 0–3, all devs)
- [ ] [C] Repo cloned, `.env` files created from `.env.example` on every machine
- [ ] [C] `docker compose up --build` runs cleanly (backend on :8000, frontend on :5173)
- [ ] [C] `GET /health` returns 200
- [ ] [C] Hero scenario seed data loads (`COMP-104 -> PO-7712 -> SUP-21 -> PROD-882`)
- [ ] [C] Team agrees on any deviations from `docs/DB_SCHEMA.md` / `API_CONTRACTS.md` /
      `TOOL_SCHEMAS.md` before writing code that depends on them

## Developer 1 — AI Agent
- [ ] [R] LLM client wired to a real provider in `agent/llm_client.py` (PS requires
      LLM API integration)
- [ ] [R] Agent dynamically chooses tools based on situation (`agent_loop.py`) —
      **not** a hardcoded sequence (PS scoring: Agent Robustness, 30%)
- [ ] [R] Full state machine implemented per `docs/AGENT_STATE_MACHINE.md`
- [ ] [R] `check_approval` tool consulted before any execution — LLM never approves
      itself (PS: >$50,000 requires human coordinator approval)
- [ ] [R] Human-readable reasoning logs written via `audit_logger.log_event()` on
      every tool call and decision (PS Core Capability #4)
- [ ] [R] Replanning: agent detects an invalidated plan and produces a new one
      (team doc Section 19E — "one of the most important advanced features")
- [ ] [REC] Supplier-lie contradiction detection (message says dispatched, tracking
      says no pickup scan) increases supplier risk and avoids blind trust
- [ ] [C] `/agent/approve` and `/agent/reject` endpoints fully wired
- [ ] [O] Background/async execution instead of blocking `/agent/trigger` call

## Developer 2 — Backend / Simulation
- [ ] [R] REST API or CLI interface exposed (PS tech constraint) — REST chosen
- [ ] [R] Real-time tool execution against a simulated environment (PS Core Capability #3)
- [ ] [C] All 8 tables created (`inventory, suppliers, purchase_orders,
      production_orders, rfqs, supplier_messages, incidents, audit_logs`)
- [ ] [C] Seed data at target scale (~20 components, 10–20 suppliers, 20–40 POs,
      5–10 production orders) built around the hero chain
- [ ] [C] Supplier simulator returns realistic RFQ quotes, messages, and tracking status
- [ ] [C] Disruption injector supports all 5 scenario types
- [ ] [C] `update_erp` actually writes purchase_orders / inventory changes
- [ ] [C] CORS configured so the frontend dev server can call the API
- [ ] [O] `/inventory/{id}/adjust`, `/suppliers/{id}/messages`,
      `/incidents/{id}/activity` convenience endpoints

## Developer 3 — Decision Engine
- [ ] [R] Severity triage / classification logic (PS Core Capability #1)
- [ ] [R] Multi-modal re-routing evaluation against SLA + cost (PS Core Capability #2)
      — even if "multi-modal" is simplified to multi-supplier for the 18h scope, this
      should be explicitly noted as a scoping decision, not silently dropped
- [ ] [R] Constraint validation: budget, quality certification, delivery deadline, MOQ
      (PS Core Capability #3 + team doc Section 8)
- [ ] [R] `days_of_supply` / production risk calculation implemented and correct
- [ ] [R] Approval threshold enforced deterministically at >$50,000 (PS exact figure)
- [ ] [C] Supplier scoring combines quality/reliability/delivery/cost with tuned weights
- [ ] [C] Split-sourcing recovery option generated when no single supplier is optimal
      (team doc Section 9)
- [ ] [C] Rejected options are still returned with a human-readable rejection reason
      (never silently dropped — judges want to see them, team doc Section 15)
- [ ] [C] Replanning invalidation check (`replanning.py`) working against live incidents
- [ ] [O] Hazardous-material transport rule check (only if hero scenario needs it —
      confirm with team; PS mentions it but hero chain may not require it)

## Developer 4 — Frontend
- [ ] [C] Control Tower shell: sidebar + top bar + routed pages
- [ ] [C] Overview dashboard: KPI cards, active incidents list, agent activity feed
- [ ] [R] Incident Command Center: inventory/production/supplier info cards + live
      agent activity + recovery plan (this is the PS's required "Explainability
      Output" surfaced visually, PS scoring: Audit Logging/Transparency/UX, 10%)
- [ ] [R] Recovery Plan panel shows all options including rejected ones with reasons
- [ ] [R] Approval UI: cost vs. threshold, reasoning, alternatives considered,
      Approve/Reject buttons wired to the backend
- [ ] [R] Audit timeline page renders the full chronological trail
- [ ] [C] Disruption Simulator panel with all 5 inject buttons
- [ ] [C] Live polling (or better) so activity feed updates without manual refresh
      during the demo
- [ ] [O] KPI card real aggregation (financial exposure, production coverage) instead
      of placeholders — needs a Dev2/Dev3-provided summary endpoint

## Cross-cutting / Integration
- [ ] [C] Hour 3 checkpoint: React -> FastAPI -> SQLite roundtrip works
- [ ] [C] Hour 6 checkpoint: inject disruption -> agent detects -> tool calls visible in UI
- [ ] [C] Hour 10 checkpoint: full pipeline demo (disruption -> investigation ->
      supplier contact -> RFQ -> plan -> approval -> ERP update) works once, even if rough
- [ ] [C] Hour 13 checkpoint: replanning + supplier contradiction + split sourcing added
- [ ] [C] Hour 15: stress test — inject 2+ overlapping disruptions, confirm no crash
- [ ] [C] Hour 16: demo freeze — no new features past this point
- [ ] [R] Explainability check: every number a judge sees on screen traces back to a
      tool result, never to LLM free text (team doc Section 4 golden rule)
