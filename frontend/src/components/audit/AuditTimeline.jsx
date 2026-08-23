/**
 * src/components/audit/AuditTimeline.jsx
 * Owner: Developer 4 (Frontend)
 */
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { listAuditLogs } from "../../api/audit.js";
import ActivityFeed from "./ActivityFeed.jsx";

export default function AuditTimeline() {
  const [logs, setLogs] = useState([]);
  const [incidentFilter, setIncidentFilter] = useState("ALL");

  useEffect(() => {
    const load = () => listAuditLogs().then(setLogs).catch(console.error);
    load();
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, []);

  const incidentIds = useMemo(() => [...new Set(logs.map((l) => l.incident_id).filter(Boolean))], [logs]);
  const filtered = useMemo(
    () => (incidentFilter === "ALL" ? logs : logs.filter((l) => l.incident_id === incidentFilter)),
    [logs, incidentFilter]
  );

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Audit Timeline</h1>
          <div className="page-subtitle">Every disruption, investigation, decision, and approval — in order.</div>
        </div>
        {incidentIds.length > 0 && (
          <select value={incidentFilter} onChange={(e) => setIncidentFilter(e.target.value)}>
            <option value="ALL">All incidents</option>
            {incidentIds.map((id) => <option key={id} value={id}>{id}</option>)}
          </select>
        )}
      </div>

      <div className="panel elevated-panel">
        {filtered.length === 0 ? (
          <p className="empty-state">No audit events yet.</p>
        ) : (
          [...filtered].reverse().map((log, i) => (
            <div key={i} style={{ padding: "12px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 13 }}>
              <div style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                {new Date(log.timestamp).toLocaleString()} ·{" "}
                {log.incident_id ? (
                  <Link to={`/incidents/${log.incident_id}`} style={{ color: "var(--text-muted)" }}>{log.incident_id}</Link>
                ) : "—"}
                {log.tool && <span> · {log.tool}</span>}
              </div>
              <div style={{ marginTop: 2 }}>{log.action}</div>
              {log.decision && <div style={{ color: "var(--accent-2)", marginTop: 2 }}>Decision: {log.decision} — {log.reason}</div>}
              {log.result && <div style={{ color: "var(--text-secondary)", marginTop: 2 }}>{log.result}</div>}
            </div>
          ))
        )}
      </div>
      <ActivityFeed logs={logs} showFilters title="Audit history" />
    </div>
  );
}