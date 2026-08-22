# API Contracts

Owner: Developer 2 (Backend / Simulation) implements; Developer 1 (agent-facing) and
Developer 4 (frontend-facing) consume. All routers live in `backend/app/api/`.
Base path in dev: `http://localhost:8000`. Swagger UI: `http://localhost:8000/docs`.

Response shapes referenced below are Pydantic models in `backend/app/schemas/`.

## Inventory — `routes_inventory.py`
| Method | Path | Response | Notes |
|---|---|---|---|
| GET | `/inventory/` | `InventoryOut[]` | includes computed `days_of_supply` |
| GET | `/inventory/{component_id}` | `InventoryOut` | 404 if missing |
| POST | `/inventory/{component_id}/adjust` | TBD | **TODO (Dev2)** — used by `update_erp` |

## Suppliers — `routes_suppliers.py`
| Method | Path | Response |
|---|---|---|
| GET | `/suppliers/` | `SupplierOut[]` |
| GET | `/suppliers/{supplier_id}` | `SupplierOut` |
| GET | `/suppliers/{supplier_id}/messages` | TBD — **TODO (Dev2)** |

## Production — `routes_production.py`
| Method | Path | Response |
|---|---|---|
| GET | `/production/` | `ProductionOrderOut[]` |
| GET | `/production/{production_id}` | `ProductionOrderOut` |
| GET | `/production/{id}/risk` | TBD — **TODO (Dev3 logic, Dev2 route)** |

## Incidents — `routes_incidents.py`
| Method | Path | Response |
|---|---|---|
| GET | `/incidents/` | `IncidentOut[]` |
| GET | `/incidents/{incident_id}` | `IncidentOut` |
| GET | `/incidents/{id}/activity` | TBD — **TODO (Dev1/Dev2)**, scoped audit feed |

## Audit — `routes_audit.py`
| Method | Path | Response |
|---|---|---|
| GET | `/audit/` | `AuditLogOut[]` |
| GET | `/audit/?incident_id=INC-001` | `AuditLogOut[]` scoped to one incident |

## Agent — `routes_agent.py`  (Dev1 owns behavior, Dev2 owns FastAPI plumbing)
| Method | Path | Body | Response | Notes |
|---|---|---|---|---|
| POST | `/agent/trigger` | `{incident_id}` | agent run summary | starts/resumes the loop |
| GET | `/agent/state/{incident_id}` | — | `{incident_id, state}` | mirrors `AgentState` |
| GET | `/agent/plan/{incident_id}` | — | `RecoveryPlan` | 404 until `PLAN_READY` |
| POST | `/agent/approve` | `{incident_id, approver}` | TBD | **TODO (Dev1)** |
| POST | `/agent/reject` | `{incident_id, approver}` | TBD | **TODO (Dev1)** |

## Simulator — `routes_simulator.py`
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/simulator/inject` | `{scenario}` | `IncidentOut` (the newly created incident) |

Valid `scenario` values: `SUPPLIER_DELAY`, `STALE_INVENTORY`, `SUPPLIER_LIE`,
`QUALITY_FAILURE`, `BUDGET_OVERRUN`.

## Change process
If you need to change a request/response shape:
1. Edit the Pydantic model in `backend/app/schemas/`.
2. Update this file.
3. Post in the team channel — Dev4's frontend and Dev1's agent both depend on these
   shapes staying stable mid-hackathon.
