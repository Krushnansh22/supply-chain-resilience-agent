/**
 * src/components/overview/AgentActivityFeed.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `auditLogs` prop (from GET /audit, shape: schemas/common.AuditLogOut)
 * Renders the safe, human-readable narration only (team doc Section 14) —
 * NEVER shows raw LLM output, only the `action` field written by audit_logger.log_event().
 */
export default function AgentActivityFeed({ auditLogs }) {
  const recent = auditLogs.slice(-12).reverse();

  return (
    <div className="panel">
      <h3>Agent Activity</h3>
      <div className="agent-activity" style={{ border: "none", padding: 0, boxShadow: "none" }}>
        {recent.length === 0 && <p className="empty-state">No agent activity yet.</p>}
        {recent.map((log, i) => (
          <div key={i} className="agent-item">
            <span className="agent-dot" />
            <span style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: 11 }}>
              {new Date(log.timestamp).toLocaleTimeString()}
            </span>
            <span>{log.action}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
