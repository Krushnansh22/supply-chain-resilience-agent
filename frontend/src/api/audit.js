/**
 * src/api/audit.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_audit.py (Dev2)
 */
import { apiRequest } from "./client.js";

export const listAuditLogs = (incidentId) =>
  apiRequest(incidentId ? `/audit/?incident_id=${incidentId}` : "/audit/");
