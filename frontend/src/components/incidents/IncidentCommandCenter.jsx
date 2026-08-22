/**
 * src/components/incidents/IncidentCommandCenter.jsx
 * Owner: Developer 4 (Frontend)
 *
 * THE main demo screen (team doc Section 13). Everything about one active
 * disruption in one place: incident summary, InfoCards (inventory/production/
 * supplier), live agent activity, RecoveryPlanPanel, and the ApprovalModal
 * when human-in-the-loop is required.
 *
 * RECEIVES: incidentId from the route (/incidents/:incidentId)
 *   - GET /incidents/{id}          -> incident summary
 *   - GET /agent/state/{id}        -> current AgentState
 *   - GET /audit/?incident_id={id} -> scoped activity feed
 *   - GET /agent/plan/{id}         -> RecoveryPlan (once PLAN_READY)
 * DELIVERS: POST /agent/trigger, /agent/approve, /agent/reject via user actions
 */
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getIncident } from "../../api/incidents.js";
import { listAuditLogs } from "../../api/audit.js";
import { getAgentState, getAgentPlan, triggerAgent } from "../../api/agent.js";

import InfoCards from "./InfoCards.jsx";
import RecoveryPlanPanel from "./RecoveryPlanPanel.jsx";
import ApprovalModal from "./ApprovalModal.jsx";

export default function IncidentCommandCenter() {
  const { incidentId } = useParams();
  const [incident, setIncident] = useState(null);
  const [agentState, setAgentState] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    // TODO (Dev4): replace one-shot load with polling (e.g. every 2s) so the
    // Agent Activity section updates live as agent_loop.py progresses — this is
    // the single most important piece of "wow factor" for judges.
    getIncident(incidentId).then(setIncident).catch(console.error);
    getAgentState(incidentId).then((r) => setAgentState(r.state)).catch(console.error);
    listAuditLogs(incidentId).then(setAuditLogs).catch(console.error);
    getAgentPlan(incidentId).then(setPlan).catch(() => setPlan(null));
  }, [incidentId]);

  if (!incident) return <p>Loading incident…</p>;

  return (
    <div>
      <div className="panel">
        <h2>{incident.affected_po || incident.incident_id} — {incident.type.replaceAll("_", " ")}</h2>
        <p>Status: <strong>{incident.status}</strong> · Severity: <strong>{incident.severity}</strong></p>
        <button onClick={() => triggerAgent(incidentId).catch(console.error)}>
          ▶ Trigger Agent
        </button>
      </div>

      <InfoCards incident={incident} />

      <div className="panel" style={{ marginTop: 16 }}>
        <h3>Agent Activity</h3>
        {auditLogs.map((log, i) => (
          <div key={i} style={{ fontSize: 13, fontFamily: "var(--font-mono)", padding: "4px 0" }}>
            ✓ {log.action}
          </div>
        ))}
      </div>

      {plan && <RecoveryPlanPanel plan={plan} incidentId={incidentId} />}

      {agentState === "WAITING_APPROVAL" && plan && (
        <ApprovalModal plan={plan} incidentId={incidentId} />
      )}
    </div>
  );
}
