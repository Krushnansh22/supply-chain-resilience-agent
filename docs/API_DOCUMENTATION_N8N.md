# API Documentation for N8N Integration

This document outlines the available API endpoints in the Supply Chain Disruption Control Agent, used for n8n automation and monitoring.

## 1. Inventory Management (`/inventory`)
- `GET /inventory/`: Lists all components with computed days of supply.
  - **Returns:** List of `InventoryOut` objects.
- `GET /inventory/{component_id}`: Retrieves details for a specific component.
  - **Returns:** `InventoryOut` object.

## 2. Supplier Management (`/suppliers`)
- `GET /suppliers/`: Lists all suppliers.
  - **Returns:** List of `SupplierOut` objects.
- `GET /suppliers/{supplier_id}`: Retrieves details for a specific supplier.
  - **Returns:** `SupplierOut` object.

## 3. Production Management (`/production`)
- `GET /production/`: Lists all production orders.
  - **Returns:** List of `ProductionOrderOut` objects.
- `GET /production/{production_id}`: Retrieves details for a specific production order.
  - **Returns:** `ProductionOrderOut` object.

## 4. Incident Management (`/incidents`)
- `GET /incidents/`: Lists all incidents, ordered by creation date.
  - **Returns:** List of `IncidentOut` objects.
- `GET /incidents/{incident_id}`: Retrieves details for a specific incident.
  - **Returns:** `IncidentOut` object.

## 5. Audit Logging (`/audit`)
- `GET /audit/`: Full audit timeline.
  - **Params:** `incident_id` (optional, to filter by incident).
  - **Returns:** List of `AuditLogOut` objects.

## 6. Agent Control (`/agent`)
- `POST /agent/trigger`: Triggers the agent loop for an incident.
  - **Body:** `{"incident_id": "..."}`
- `GET /agent/state/{incident_id}`: Gets the current agent state for an incident.
- `POST /agent/approve`: Approves a pending recovery plan. (Not fully implemented).
- `POST /agent/reject`: Rejects a pending recovery plan. (Not fully implemented).

## 7. Simulator (`/simulator`)
- `POST /simulator/inject`: Injects a disruption scenario.
  - **Body:** `{"scenario": "..."}` (e.g., "SUPPLIER_DELAY").
