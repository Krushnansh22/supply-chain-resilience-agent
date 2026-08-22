/**
 * src/components/incidents/IncidentCommandCenter.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: incidentId from the route
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

  if (!incident) {
    return (
      <div className="loading-shell">
        <span className="loading-orb" />
        <span>Loading incident…</span>
      </div>
    );
  }

  const currentStepIndex = FLOW_ORDER.indexOf(agentState);

  return (
    <div>
      <div className="panel elevated-panel">
        <div className="command-header">
          <div>
            <h2>{incident.affected_po || incident.incident_id} — {incident.type.replaceAll("_", " ")}</h2>
            <div className="command-meta">
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={agentState || incident.status} />
              <span className="command-id">{incident.incident_id}</span>
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

      <div className="panel elevated-panel" style={{ marginTop: 16 }}>
        <h3>Agent Activity</h3>
        {auditLogs.length === 0 ? (
          <p className="empty-state">No activity yet — trigger the agent to begin investigating.</p>
        ) : (
          auditLogs.map((log, i) => (
            <div key={i} className="audit-line">
              <span className="audit-time">{new Date(log.timestamp).toLocaleTimeString()}</span>{" "}
              ✓ {log.action}
              {log.decision && <span className="audit-decision"> — {log.decision}: {log.reason}</span>}
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