/**
 * src/api/agent.js
 * Owner: Developer 4 (Frontend)
 * Backend contract: app/api/routes_agent.py (Dev1 behavior, Dev2 plumbing)
 */
import { apiRequest } from "./client.js";

export const scanAndTriage = () =>
  apiRequest("/agent/scan-and-triage", { method: "POST" });

export const processBacklog = () =>
  apiRequest("/agent/process-backlog", { method: "POST" });

export const getSystemStatus = () => apiRequest("/agent/system-status");

export const triggerAgent = (incidentId) =>
  apiRequest("/agent/trigger", { method: "POST", body: JSON.stringify({ incident_id: incidentId }) });

export const runIncident = (incidentId) =>
  apiRequest("/agent/run-incident", { method: "POST", body: JSON.stringify({ incident_id: incidentId }) });

export const getAgentState = (incidentId) => apiRequest(`/agent/state/${incidentId}`);

export const getAgentPlan = (incidentId) => apiRequest(`/agent/plan/${incidentId}`);

export const getAgentTasks = (incidentId) => apiRequest(`/agent/tasks/${incidentId}`);

export const getAgentAudit = (incidentId) => apiRequest(`/agent/audit/${incidentId}`);

export const replanIncident = (incidentId, invalidationReason, affectedSupplier = null) =>
  apiRequest(`/agent/replan/${incidentId}`, {
    method: "POST",
    body: JSON.stringify({
      incident_id: incidentId,
      invalidation_reason: invalidationReason,
      affected_supplier: affectedSupplier,
    }),
  });

export const approvePlan = (incidentId, revisedValue = null, revisionReason = null) => {
  const payload = { incident_id: incidentId };
  if (revisedValue !== null && revisedValue !== undefined && revisedValue !== "") {
    payload.revised_value = Number(revisedValue);
    payload.revision_reason = revisionReason || "Physical stock count verification";
  }
  return apiRequest("/agent/approve", { method: "POST", body: JSON.stringify(payload) });
};

export const rejectPlan = (incidentId) =>
  apiRequest("/agent/reject", { method: "POST", body: JSON.stringify({ incident_id: incidentId }) });
