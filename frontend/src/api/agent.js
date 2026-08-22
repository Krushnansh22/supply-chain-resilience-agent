/**
 * src/api/agent.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_agent.py (Dev1 behavior, Dev2 plumbing)
 */
import { apiRequest } from "./client.js";

export const triggerAgent = (incidentId) =>
  apiRequest("/agent/trigger", { method: "POST", body: JSON.stringify({ incident_id: incidentId }) });

export const getAgentState = (incidentId) => apiRequest(`/agent/state/${incidentId}`);

export const getAgentPlan = (incidentId) => apiRequest(`/agent/plan/${incidentId}`);

export const approvePlan = (incidentId) =>
  apiRequest("/agent/approve", { method: "POST", body: JSON.stringify({ incident_id: incidentId }) });

export const rejectPlan = (incidentId) =>
  apiRequest("/agent/reject", { method: "POST", body: JSON.stringify({ incident_id: incidentId }) });
