/**
 * src/components/approvals/ApprovalsPage.jsx
 * Owner: Developer 4 (Frontend)
 */
import { useEffect, useState } from "react";
import { listIncidents } from "../../api/incidents.js";
import { getAgentPlan } from "../../api/agent.js";
import ApprovalCard from "./ApprovalCard.jsx";
import { useAuth } from "../../context/AuthContext.jsx";

export default function ApprovalsPage() {
  const { activeWarehouse, currentUser } = useAuth();
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    listIncidents("all")
      .then(async (incidents) => {
        // Filter only WAITING_APPROVAL or DATA_INCONSISTENCY incidents
        const waiting = (incidents || []).filter(
          (i) => i.status === "WAITING_APPROVAL" || i.status === "DATA_INCONSISTENCY"
        );

        // Fetch plans in parallel and deduplicate by incident_id to eliminate redundancy
        const map = new Map();
        await Promise.all(
          waiting.map(async (incident) => {
            if (map.has(incident.incident_id)) return;
            try {
              const plan = await getAgentPlan(incident.incident_id);
              map.set(incident.incident_id, { incident, plan });
            } catch {
              map.set(incident.incident_id, {
                incident,
                plan: { incident_id: incident.incident_id, options: [], requires_human_approval: true },
              });
            }
          })
        );
        setPending(Array.from(map.values()));
      })
      .catch((err) => console.error("Approvals load failed:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 3500);
    return () => clearInterval(interval);
  }, [activeWarehouse, currentUser]);

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
          <h1>Approvals & Data Calibration</h1>
          <div className="page-subtitle">
            Escalations requiring human authorization or physical count baseline calibration.
          </div>
        </div>
      </div>

      {pending.length === 0 ? (
        <div className="panel elevated-panel">
          <p className="empty-state">
            No approvals pending. Recovery plans within the autonomous threshold execute automatically.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {pending.map(({ incident, plan }) => (
            <ApprovalCard
              key={incident.incident_id}
              plan={plan}
              incident={incident}
              onDecided={load}
            />
          ))}
        </div>
      )}
    </div>
  );
}