# Database Schema

Owner: Developer 2 (Backend / Simulation). Source of truth for table shape; if a field
is added/removed, update the SQLAlchemy model in `backend/app/models/`, this file, and
notify the team (Dev1/Dev3 read from these tables via tools; Dev4 reads via the API).

Engine: SQLite (`backend/data/scda.db`). Classification: **CHOSEN** (team doc Section 3).

## inventory
| field | type | notes |
|---|---|---|
| component_id (PK) | string | e.g. `COMP-104` |
| current_stock | int | total physical stock |
| usable_stock | int | excludes quarantined/defective units |
| daily_usage | float | used to compute `days_of_supply` |
| safety_stock | int | reorder threshold |

`days_of_supply` is **computed**, not stored — see `decision_engine/inventory_calc.py`.

## suppliers
| field | type | notes |
|---|---|---|
| supplier_id (PK) | string | e.g. `SUP-21` |
| name | string | |
| quality_score | float | 0-100 |
| reliability_score | float | 0-100 |
| certifications | string | comma-separated, e.g. `ISO9001,RoHS` |

## purchase_orders
| field | type | notes |
|---|---|---|
| po_id (PK) | string | e.g. `PO-7712` |
| component_id | string (FK-ish) | -> inventory.component_id |
| supplier_id | string (FK-ish) | -> suppliers.supplier_id |
| quantity | int | |
| expected_delivery | datetime | nullable |
| status | string | OPEN \| DELAYED \| DISPATCHED \| RECEIVED \| CANCELLED |
| unit_price | float | |

## production_orders
| field | type | notes |
|---|---|---|
| production_id (PK) | string | e.g. `PROD-882` |
| product | string | |
| component_id | string | -> inventory.component_id |
| quantity | int | |
| component_per_unit | int | |
| deadline | datetime | nullable |
| priority | string | LOW \| MEDIUM \| HIGH |
| status | string | ON_TRACK \| AT_RISK \| BLOCKED |

## rfqs
| field | type | notes |
|---|---|---|
| id (PK) | int autoincrement | |
| supplier_id | string | |
| component_id | string | |
| quantity | int | |
| unit_price | float | |
| delivery_days | int | |
| expedite_available | bool | |
| expedite_fee | float | nullable |

## supplier_messages
| field | type | notes |
|---|---|---|
| message_id (PK) | int autoincrement | |
| supplier_id | string | |
| po_id | string | nullable |
| message | string | |
| timestamp | datetime | |

## incidents
| field | type | notes |
|---|---|---|
| incident_id (PK) | string | e.g. `INC-A1B2C3` |
| type | string | SUPPLIER_DELAY \| SUPPLIER_LIE \| QUALITY_FAILURE \| BUDGET_OVERRUN \| STALE_INVENTORY |
| severity | string | LOW \| MEDIUM \| HIGH \| CRITICAL |
| affected_component | string | nullable |
| affected_po | string | nullable |
| status | string | mirrors `agent/states.py::AgentState` |
| created_at | datetime | |

## audit_logs
| field | type | notes |
|---|---|---|
| id (PK) | int autoincrement | |
| timestamp | datetime | |
| incident_id | string | nullable |
| action | string | human-readable summary |
| tool | string | nullable, tool name that produced this entry |
| result | string | nullable |
| decision | string | nullable, e.g. EXECUTE / ESCALATE / REPLAN |
| reason | string | nullable |

## Open decisions (flag in standup)
- MOQ (minimum order quantity): store per-supplier, per-RFQ, or both? — **TBD by Dev3**
- Should `update_erp` mutate `inventory.usable_stock` directly, or only create new
  `purchase_orders` rows and let inventory catch up on "receipt"? — **TBD by Dev2/Dev3**
