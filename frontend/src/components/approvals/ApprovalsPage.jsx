/**
 * src/components/approvals/ApprovalsPage.jsx
 * Owner: Developer 4 (Frontend)
 */
import { useEffect, useState } from "react";
import { listIncidents } from "../../api/incidents.js";
import { getAgentPlan } from "../../api/agent.js";
import ApprovalCard from "./ApprovalCard.jsx";

export default function ApprovalsPage() {
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    listIncidents()
      .then(async (incidents) => {
        const waiting = incidents.filter((i) => i.status === "WAITING_APPROVAL");
        const withPlans = await Promise.all(
          waiting.map(async (incident) => {
            try {
              const plan = await getAgentPlan(incident.incident_id);
              return { incident, plan };
            } catch {
              return null;
            }
          })
        );
        setPending(withPlans.filter(Boolean));
      })
      .catch((err) => console.error("Approvals load failed:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="loading-shell">
        <span className="loading-orb" />
        <span>Loading approvals…</span>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Approvals</h1>
          <div className="page-subtitle">Decisions above the autonomous-execution threshold, waiting on a human coordinator.</div>
        </div>
      </div>

      {pending.length === 0 ? (
        <div className="panel elevated-panel">
          <p className="empty-state">No approvals pending. Recovery plans within the autonomous threshold execute automatically.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {pending.map(({ incident, plan }) => (
            <ApprovalCard key={incident.incident_id} plan={plan} incident={incident} onDecided={load} />
          ))}
        </div>
      )}
    </div>
  );
}