/**
 * src/components/overview/AgentActivityFeed.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Styled to match the reference image's right-hand panel style.
 * RECEIVES: `auditLogs` prop (from GET /audit)
 */
import ActivityFeed from "../audit/ActivityFeed.jsx";

export default function AgentActivityFeed({ auditLogs }) {
  const recent = auditLogs.slice(-12).reverse();

  return (
    <div className="panel">
      {/* Panel header — matches image panel style */}
      <div className="panel-header">
        <span className="panel-title">Agent Activity</span>
        <div className="panel-actions">
          <button className="icon-btn" title="Filter" style={{ fontSize: 14 }}>⚡</button>
          <button className="icon-btn" title="More options" style={{ fontSize: 16, letterSpacing: 1 }}>···</button>
        </div>
      </div>

      <div className="agent-activity" style={{ border: "none", padding: 0, boxShadow: "none", background: "none" }}>
        {recent.length === 0 && (
          <p className="empty-state">No agent activity yet.</p>
        )}
        {recent.map((log, i) => (
          <div key={i} className="agent-item">
            <span className="agent-dot" />
            <span
              style={{
                color: "var(--text-muted)",
                fontFamily: "var(--font-mono)",
                fontSize: 10,
                flexShrink: 0,
              }}
            >
              {new Date(log.timestamp).toLocaleTimeString()}
            </span>
            <span style={{ fontSize: 12, color: "var(--text-primary)" }}>{log.action}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
