/**
 * src/components/overview/AgentActivityFeed.jsx
 * Real-time streaming feed of autonomous decisions, tool calls, and audit telemetry on the Control Tower dashboard.
 */
import React from "react";
import { Link } from "react-router-dom";

export default function AgentActivityFeed({ auditLogs = [] }) {
  // Sort newest first
  const recent = [...auditLogs]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 10);

  const getTagStyle = (log) => {
    if (log.decision === "AUTONOMOUS_RESOLVED" || (log.action && log.action.toLowerCase().includes("autonomous"))) {
      return { bg: "rgba(16, 185, 129, 0.15)", color: "#10B981", border: "1px solid rgba(16, 185, 129, 0.4)", label: "🤖 AUTO" };
    }
    if (log.tool) {
      return { bg: "rgba(139, 92, 246, 0.15)", color: "#A78BFA", border: "1px solid rgba(139, 92, 246, 0.4)", label: `🔧 ${log.tool}` };
    }
    if (log.decision === "STOCK_CORRECTED" || log.decision === "APPROVED" || log.decision === "WAITING_APPROVAL") {
      return { bg: "rgba(245, 158, 11, 0.15)", color: "#F59E0B", border: "1px solid rgba(245, 158, 11, 0.4)", label: "👤 APPROVAL" };
    }
    return { bg: "rgba(35, 184, 201, 0.15)", color: "#23B8C9", border: "1px solid rgba(35, 184, 201, 0.4)", label: "DECISION" };
  };

  return (
    <div className="panel elevated-panel" style={{ padding: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16 }}>Live Agent Activity</h3>
          <span style={{ fontSize: 11, color: "#94A3B8" }}>Streaming decisions & tool calls</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              display: "inline-block",
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#10B981",
              boxShadow: "0 0 8px #10B981",
            }}
          />
          <span style={{ fontSize: 10, fontWeight: 700, color: "#10B981", letterSpacing: "0.5px" }}>LIVE</span>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {recent.length === 0 ? (
          <p className="empty-state" style={{ color: "#64748B", textAlign: "center", padding: 20 }}>
            No agent activity recorded yet. Start agent or inject a scenario.
          </p>
        ) : (
          recent.map((log, i) => {
            const tag = getTagStyle(log);
            return (
              <div
                key={i}
                style={{
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  borderRadius: 8,
                  padding: 10,
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                  transition: "background 0.15s ease",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span
                      style={{
                        fontSize: 9,
                        fontWeight: 800,
                        padding: "1px 6px",
                        borderRadius: 4,
                        background: tag.bg,
                        color: tag.color,
                        border: tag.border,
                        letterSpacing: "0.5px",
                      }}
                    >
                      {tag.label}
                    </span>
                    {log.incident_id && (
                      <Link
                        to={`/incidents/${log.incident_id}`}
                        style={{ fontSize: 11.5, fontWeight: 700, color: "#23B8C9", textDecoration: "none" }}
                      >
                        {log.incident_id}
                      </Link>
                    )}
                  </div>
                  <span style={{ color: "#64748B", fontFamily: "JetBrains Mono, monospace", fontSize: 10 }}>
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div style={{ fontSize: 12.5, color: "#F1F5F9", fontWeight: 600, lineHeight: 1.4 }}>
                  {log.action || log.decision || "Agent Event"}
                </div>

                {log.reason && (
                  <div style={{ fontSize: 11.5, color: "#94A3B8", lineHeight: 1.3 }}>
                    💡 <em>{log.reason}</em>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {auditLogs.length > 10 && (
        <Link
          to="/agent-activity"
          style={{
            display: "block",
            textAlign: "center",
            marginTop: 14,
            color: "#23B8C9",
            fontWeight: 600,
            fontSize: 12,
            textDecoration: "none",
          }}
        >
          View full agent telemetry stream ({auditLogs.length} events) →
        </Link>
      )}
    </div>
  );
}
