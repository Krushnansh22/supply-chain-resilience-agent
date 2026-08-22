/**
 * src/components/audit/AuditTimeline.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 17: full chronological audit trail across all incidents.
 * RECEIVES: GET /audit (src/api/audit.js) -> schemas/common.AuditLogOut[]
 */
import { useEffect, useState } from "react";
import { listAuditLogs } from "../../api/audit.js";

export default function AuditTimeline() {
  const [logs, setLogs] = useState([]);

  useEffect(() => { listAuditLogs().then(setLogs).catch(console.error); }, []);

  return (
    <div className="panel">
      <h2>Audit Timeline</h2>
      {logs.map((log, i) => (
        <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", fontSize: 13 }}>
          <div style={{ fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
            {new Date(log.timestamp).toLocaleString()} · {log.incident_id || "—"}
          </div>
          <div>{log.action}</div>
          {log.decision && <div style={{ color: "var(--accent)" }}>Decision: {log.decision} — {log.reason}</div>}
        </div>
      ))}
    </div>
  );
}
