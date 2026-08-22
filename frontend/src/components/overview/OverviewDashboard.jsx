/**
 * src/components/overview/OverviewDashboard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * First screen judges see (team doc Section 12). Composes:
 *   - KpiCards (active incidents, production coverage, financial exposure, continuity)
 *   - ActiveIncidentsList (clickable -> IncidentCommandCenter)
 *   - AgentActivityFeed (recent audit log entries across all incidents)
 *
 * RECEIVES: GET /incidents, GET /audit (via src/api/incidents.js, src/api/audit.js)
 * DELIVERS: nothing further downstream — this is a leaf page
 */
import { useEffect, useState } from "react";
import { listIncidents } from "../../api/incidents.js";
import { listAuditLogs } from "../../api/audit.js";
import KpiCards from "./KpiCards.jsx";
import ActiveIncidentsList from "./ActiveIncidentsList.jsx";
import AgentActivityFeed from "./AgentActivityFeed.jsx";

export default function OverviewDashboard() {
  const [incidents, setIncidents] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO (Dev4): switch to polling (setInterval) or SSE/websocket once the agent
    // loop can push events, so the "AGENT ACTIVITY" feed updates live during the demo.
    Promise.all([listIncidents(), listAuditLogs()])
      .then(([incidentsRes, auditRes]) => {
        setIncidents(incidentsRes);
        setAuditLogs(auditRes);
      })
      .catch((err) => console.error("Overview load failed:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading control tower…</p>;

  return (
    <div>
      <KpiCards incidents={incidents} />
      <div style={{ display: "flex", gap: 16, marginTop: 24 }}>
        <div style={{ flex: 2 }}>
          <ActiveIncidentsList incidents={incidents} />
        </div>
        <div style={{ flex: 1 }}>
          <AgentActivityFeed auditLogs={auditLogs} />
        </div>
      </div>
    </div>
  );
}
