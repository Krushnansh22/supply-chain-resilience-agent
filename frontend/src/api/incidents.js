/**
 * src/api/incidents.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_incidents.py (Dev2)
 */
import { apiRequest } from "./client.js";

export const listIncidents = () => apiRequest("/incidents/");
export const getIncident = (incidentId) => apiRequest(`/incidents/${incidentId}`);

// routes_incidents.py now exposes this scoped endpoint — use it instead of
// filtering the global /audit/ feed client-side wherever we only need one incident.
export const getIncidentActivity = (incidentId) => apiRequest(`/incidents/${incidentId}/activity`);
