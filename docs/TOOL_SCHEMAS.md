# Agent Tool Schemas

Owner: Developer 1 (Agent) owns `backend/app/agent/tool_schemas.py`, which MUST mirror
this table exactly (the LLM only sees `tool_schemas.py` — this doc is the human-readable
mirror). Underlying implementations live in `backend/app/tools/`, split between
Developer 2 (I/O: DB reads/writes, simulated supplier calls) and Developer 3 (business
math: constraint checks, scoring, recovery planning).

Every tool returns a `ToolResult` (`backend/app/schemas/tool_io.py`):
`{tool_name, success, data, summary, error}`. `summary` is what gets written to the
audit log and shown in the UI — keep it short and factual.

| Tool | Params | Implemented in | Wraps |
|---|---|---|---|
| `get_inventory` | `component_id` | `tools/inventory_tools.py` (Dev2) | `decision_engine/inventory_calc.py` (Dev3) |
| `get_production_orders` | `component_id` | `tools/production_tools.py` (Dev2) | `decision_engine/production_risk.py` (Dev3) |
| `get_supplier` | `supplier_id` | `tools/supplier_tools.py` (Dev2) | — |
| `send_supplier_message` | `supplier_id, po_id, message` | `tools/supplier_tools.py` (Dev2) | `simulator/supplier_simulator.py` (Dev2) |
| `get_tracking_status` | `po_id` | `tools/supplier_tools.py` (Dev2) | `simulator/supplier_simulator.py` (Dev2) |
| `request_rfq` | `component_id, quantity, supplier_ids[]` | `tools/rfq_tools.py` (Dev2) | `simulator/supplier_simulator.py` (Dev2) |
| `build_recovery_plan` | `required_quantity, required_cert?, required_by_days` | **TODO** — wire in `agent/tool_executor.py` | `decision_engine/recovery_planner.py` (Dev3) |
| `check_approval` | `cost` | `tools/approval_tools.py` (Dev3 rule, Dev2 route) | `config.settings.AUTONOMOUS_APPROVAL_LIMIT_USD` |
| `update_erp` | `incident_id, option_id` | **TODO** — wire in `agent/tool_executor.py` | `tools/erp_tools.py` (Dev2) |

## Golden rule
The LLM **never** computes cost totals, days-of-supply, or approval thresholds itself.
It only calls a tool and narrates the tool's `summary`. See team doc Section 4 and
`agent/prompts.py::SYSTEM_PROMPT` rule #1.

## Adding a new tool — checklist
1. Implement the function in the right file under `backend/app/tools/` (or a new file).
2. Add its JSON schema entry to `backend/app/agent/tool_schemas.py`.
3. Add a dispatch branch in `backend/app/agent/tool_executor.py`.
4. Add a row to the table above.
5. If it should be user-triggerable outside the agent, add a REST route too and note it
   in `API_CONTRACTS.md`.
