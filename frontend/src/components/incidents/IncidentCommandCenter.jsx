/**
 * src/components/incidents/IncidentCommandCenter.jsx
 * Owner: Developer 4 (Frontend)
 *
 * THE main demo screen (team doc Section 13). Everything about one active
 * disruption in one place: incident summary, InfoCards (inventory/production/
 * supplier), live agent activity, RecoveryPlanPanel, and the ApprovalModal
 * when human-in-the-loop is required. The flow strip at the top mirrors the
 * required narrative: Disruption -> Investigation -> Agent Actions ->
 * Recovery Options -> Decision -> Approval -> ERP Update -> Audit.
 *
 * RECEIVES: incidentId from the route (/incidents/:incidentId)
 *   - GET /incidents/{id}                 -> incident summary
 *   - GET /agent/state/{id}                -> current AgentState
 *   - GET /incidents/{id}/activity         -> scoped activity feed
 *   - GET /agent/plan/{id}                 -> RecoveryPlan (once PLAN_READY)
 * DELIVERS: POST /agent/trigger, /agent/approve, /agent/reject via user actions
 */
import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getIncident, getIncidentActivity } from "../../api/incidents.js";
import { getAgentState, getAgentPlan, triggerAgent } from "../../api/agent.js";

import SeverityBadge from "../common/SeverityBadge.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import InfoCards from "./InfoCards.jsx";
import RecoveryPlanPanel from "./RecoveryPlanPanel.jsx";
import ApprovalModal from "./ApprovalModal.jsx";

const FLOW_STEPS = [
  { key: "DETECTED", label: "Disruption" },
  { key: "INVESTIGATING", label: "Investigation" },
  { key: "SUPPLIER_CONTACT", label: "Agent Actions" },
  { key: "EVALUATING", label: "Recovery Options" },
  { key: "PLAN_READY", label: "Decision" },
  { key: "WAITING_APPROVAL", label: "Approval" },
  { key: "EXECUTING", label: "ERP Update" },
  { key: "RESOLVED", label: "Audit" },
];
const FLOW_ORDER = FLOW_STEPS.map((s) => s.key);

export default function IncidentCommandCenter() {
  const { incidentId } = useParams();
  const [incident, setIncident] = useState(null);
  const [agentState, setAgentState] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [plan, setPlan] = useState(null);
  const [triggerError, setTriggerError] = useState(null);
  const [triggering, setTriggering] = useState(false);

  const refresh = useCallback(() => {
    getIncident(incidentId).then(setIncident).catch(console.error);
    getAgentState(incidentId).then((r) => setAgentState(r.state)).catch(console.error);
    getIncidentActivity(incidentId).then(setAuditLogs).catch(console.error);
    getAgentPlan(incidentId).then(setPlan).catch(() => setPlan(null));
  }, [incidentId]);

  useEffect(() => {
    refresh();
    // Poll while the demo is running so Agent Activity updates live as
    // agent_loop.py progresses — the single biggest "wow factor" for judges.
    // Stops once the incident resolves (or on unmount) to avoid needless load.
    const interval = setInterval(() => {
      if (agentState !== "RESOLVED") refresh();
    }, 3000);
    return () => clearInterval(interval);
  }, [refresh, agentState]);

  const handleTrigger = async () => {
    setTriggering(true);
    setTriggerError(null);
    try {
      await triggerAgent(incidentId);
      refresh();
    } catch (err) {
      setTriggerError(err.message || "Failed to trigger agent.");
    } finally {
      setTriggering(false);
    }
  };

  if (!incident) return <p>Loading incident…</p>;

  const currentStepIndex = FLOW_ORDER.indexOf(agentState);

  return (
    <div>
      <div className="panel">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
          <div>
            <h2>{incident.affected_po || incident.incident_id} — {incident.type.replaceAll("_", " ")}</h2>
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={agentState || incident.status} />
              <span style={{ color: "var(--text-muted)", fontSize: 12 }}>{incident.incident_id}</span>
            </div>
          </div>
          <button className="btn-primary" disabled={triggering} onClick={handleTrigger}>
            {triggering ? "Triggering…" : "▶ Trigger Agent"}
          </button>
        </div>

        <div className="flow-strip">
          {FLOW_STEPS.map((step, i) => (
            <span key={step.key} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span className={`flow-step${i <= currentStepIndex ? " active" : ""}`}>{step.label}</span>
              {i < FLOW_STEPS.length - 1 && <span className="flow-sep">→</span>}
            </span>
          ))}
        </div>

        {triggerError && <div className="error-banner">{triggerError}</div>}
      </div>

      <InfoCards incident={incident} plan={plan} />

      <div className="panel" style={{ marginTop: 16 }}>
        <h3>Agent Activity</h3>
        {auditLogs.length === 0 ? (
          <p className="empty-state">No activity yet — trigger the agent to begin investigating.</p>
        ) : (
          auditLogs.map((log, i) => (
            <div key={i} style={{ fontSize: 13, fontFamily: "var(--font-mono)", padding: "4px 0" }}>
              <span style={{ color: "var(--text-muted)" }}>{new Date(log.timestamp).toLocaleTimeString()}</span>{" "}
              ✓ {log.action}
              {log.decision && <span style={{ color: "var(--accent)" }}> — {log.decision}: {log.reason}</span>}
            </div>
          ))
        )}
      </div>

      {plan && <RecoveryPlanPanel plan={plan} incidentId={incidentId} onExecuted={refresh} />}

      {agentState === "WAITING_APPROVAL" && plan && (
        <ApprovalModal plan={plan} incidentId={incidentId} onDecided={refresh} />
      )}
    </div>
  );
}
