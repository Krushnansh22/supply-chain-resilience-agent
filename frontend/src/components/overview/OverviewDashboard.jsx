/**
 * src/components/overview/OverviewDashboard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * First screen judges see (team doc Section 12). Composes:
 *   - KpiCards (active/critical incidents, production-at-risk, pending approvals)
 *   - ActiveIncidentsList (clickable -> IncidentCommandCenter)
 *   - AgentActivityFeed (recent audit log entries across all incidents)
 *
 * RECEIVES: GET /incidents, GET /production, GET /audit
 *   (via src/api/incidents.js, src/api/production.js, src/api/audit.js)
 * DELIVERS: nothing further downstream — this is a leaf page
 */
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listIncidents } from "../../api/incidents.js";
import { listAuditLogs } from "../../api/audit.js";
import { listProductionOrders } from "../../api/production.js";
import KpiCards from "./KpiCards.jsx";
import ActiveIncidentsList from "./ActiveIncidentsList.jsx";
import AgentActivityFeed from "./AgentActivityFeed.jsx";

export default function OverviewDashboard() {
  const [incidents, setIncidents] = useState([]);
  const [productionOrders, setProductionOrders] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    Promise.all([listIncidents(), listAuditLogs(), listProductionOrders()])
      .then(([incidentsRes, auditRes, productionRes]) => {
        setIncidents(incidentsRes);
        setAuditLogs(auditRes);
        setProductionOrders(productionRes);
      })
      .catch((err) => console.error("Overview load failed:", err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    // Light polling so the control tower reflects the agent loop live during
    // a demo without requiring a manual refresh between simulator clicks.
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [load]);

  if (loading) return <p>Loading control tower…</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Control Tower</h1>
          <div className="page-subtitle">Live view of active supply-chain disruptions and agent decisions.</div>
        </div>
        <Link to="/simulator" className="btn btn-primary" style={{ textDecoration: "none" }}>
          ⚡ Simulate Disruption
        </Link>
      </div>

      <KpiCards incidents={incidents} productionOrders={productionOrders} />
      <div style={{ display: "flex", gap: 16, marginTop: 24, flexWrap: "wrap" }}>
        <div style={{ flex: 2, minWidth: 320 }}>
          <ActiveIncidentsList incidents={incidents} />
        </div>
        <div style={{ flex: 1, minWidth: 260 }}>
          <AgentActivityFeed auditLogs={auditLogs} />
        </div>
      </div>
    </div>
  );
}
