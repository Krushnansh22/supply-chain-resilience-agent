/**
 * Safe, operator-facing view of agent decisions and tool activity.
 * Raw model chain-of-thought is intentionally not persisted or displayed.
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listAuditLogs } from "../../api/audit.js";

export default function AgentActivityPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const load = () => listAuditLogs().then((items) => {
      if (mounted) setLogs(items);
    }).catch(console.error).finally(() => {
      if (mounted) setLoading(false);
    });
    load();
    const interval = setInterval(load, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Agent Activity</h1>
          <div className="page-subtitle">Live decisions, state changes, tool calls, and outcomes.</div>
        </div>
        <span className="badge badge-info">AUTO-REFRESH 5S</span>
      </div>

      <div className="panel">
        {loading ? <p className="empty-state">Loading activity…</p> : logs.length === 0 ? (
          <p className="empty-state">No agent activity yet.</p>
        ) : [...logs].reverse().map((log, index) => (
          <div key={`${log.timestamp}-${index}`} style={{ padding: "12px 0", borderBottom: "1px solid var(--border-subtle)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", fontSize: 12 }}>
              <span style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                {new Date(log.timestamp).toLocaleString()}
              </span>
              <span style={{ color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}>
                {log.tool ? `TOOL · ${log.tool}` : "AGENT EVENT"}
                {log.incident_id && <> · <Link to={`/incidents/${log.incident_id}`}>{log.incident_id}</Link></>}
              </span>
            </div>
            <div style={{ marginTop: 5 }}>{log.action}</div>
            {log.decision && <div style={{ color: "var(--accent)", fontSize: 13, marginTop: 3 }}>Decision: {log.decision}</div>}
            {log.reason && <div style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 3 }}>{log.reason}</div>}
            {log.result && <div style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 3 }}>Result: {log.result}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}