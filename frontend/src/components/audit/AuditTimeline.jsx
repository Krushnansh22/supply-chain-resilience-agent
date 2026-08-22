/**
 * src/components/audit/AuditTimeline.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 17: full chronological audit trail across all incidents.
 * RECEIVES: GET /audit (src/api/audit.js) -> schemas/common.AuditLogOut[]
 */
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { listAuditLogs } from "../../api/audit.js";

export default function AuditTimeline() {
  const [logs, setLogs] = useState([]);
  const [incidentFilter, setIncidentFilter] = useState("ALL");

  useEffect(() => { listAuditLogs().then(setLogs).catch(console.error); }, []);

  const incidentIds = useMemo(
    () => [...new Set(logs.map((l) => l.incident_id).filter(Boolean))],
    [logs]
  );
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

      <div className="panel">
        {filtered.length === 0 ? (
          <p className="empty-state">No audit events yet.</p>
        ) : (
          [...filtered].reverse().map((log, i) => (
            <div key={i} style={{ padding: "10px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 13 }}>
              <div style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                {new Date(log.timestamp).toLocaleString()} ·{" "}
                {log.incident_id ? (
                  <Link to={`/incidents/${log.incident_id}`} style={{ color: "var(--text-muted)" }}>{log.incident_id}</Link>
                ) : "—"}
                {log.tool && <span> · {log.tool}</span>}
              </div>
              <div>{log.action}</div>
              {log.decision && <div style={{ color: "var(--accent)" }}>Decision: {log.decision} — {log.reason}</div>}
              {log.result && <div style={{ color: "var(--text-secondary)" }}>{log.result}</div>}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
