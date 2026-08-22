/**
 * src/components/overview/AgentActivityFeed.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `auditLogs` prop (from GET /audit, shape: schemas/common.AuditLogOut)
 * Renders the safe, human-readable narration only (team doc Section 14) —
 * NEVER shows raw LLM output, only the `action` field written by audit_logger.log_event().
 */
export default function AgentActivityFeed({ auditLogs }) {
  return (
    <div className="panel">
      <h3>Agent Activity</h3>
      {auditLogs.slice(-10).reverse().map((log, i) => (
        <div key={i} style={{ fontSize: 13, padding: "4px 0", fontFamily: "var(--font-mono)" }}>
          <span style={{ color: "var(--text-muted)" }}>
            {new Date(log.timestamp).toLocaleTimeString()}
          </span>{" "}
          {log.action}
        </div>
      ))}
    </div>
  );
}
