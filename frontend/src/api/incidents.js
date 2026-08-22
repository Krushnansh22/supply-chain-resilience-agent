/**
 * src/api/incidents.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_incidents.py (Dev2)
 */
import { apiRequest } from "./client.js";

export const listIncidents = () => apiRequest("/incidents/");
export const getIncident = (incidentId) => apiRequest(`/incidents/${incidentId}`);

// TODO (Dev4): once routes_incidents.py exposes GET /incidents/{id}/activity, add it here.
