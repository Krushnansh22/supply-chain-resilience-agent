import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";

function eventType(log) {
  if (log.tool) return "TOOL";
  if (log.decision === "AUTONOMOUS_RESOLVED" || log.decision === "STOCK_CORRECTED" || log.decision === "APPROVED" || log.decision === "PLAN_GENERATED") return "DECISION";
  if (log.decision) return "DECISION";
  if (log.action?.toLowerCase().includes("transition")) return "STATE";
  return "EVENT";
}

const TYPE_LABELS = {
  ALL: "🌐 All Activity",
  AUTONOMOUS: "🤖 Autonomous Decisions",
  TOOL: "🔧 Tool Calls & Telemetry",
  DECISION: "📊 All Decisions",
  HUMAN: "👤 Human Approvals",
};

export default function ActivityFeed({ logs = [], compact = false, showFilters = false, title = "Activity" }) {
  const [filterMode, setFilterMode] = useState("ALL");
  const [incidentFilter, setIncidentFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [expanded, setExpanded] = useState(() => new Set());

  const incidents = useMemo(() => [...new Set(logs.map((log) => log.incident_id).filter(Boolean))], [logs]);

  const filtered = useMemo(() => {
    return [...logs]
      .filter((log) => {
        if (filterMode === "ALL") return true;
        if (filterMode === "AUTONOMOUS") {
          return log.decision === "AUTONOMOUS_RESOLVED" || log.decision === "ERP_UPDATED" || (log.action && log.action.toLowerCase().includes("autonomous"));
        }
        if (filterMode === "TOOL") return !!log.tool;
        if (filterMode === "DECISION") return !!log.decision;
        if (filterMode === "HUMAN") {
          return log.decision === "STOCK_CORRECTED" || log.decision === "APPROVED" || log.decision === "WAITING_APPROVAL" || (log.action && log.action.toLowerCase().includes("human"));
        }
        return true;
      })
      .filter((log) => incidentFilter === "ALL" || log.incident_id === incidentFilter)
      .filter((log) => {
        if (!searchQuery) return true;
        const q = searchQuery.toLowerCase();
        return (
          (log.action && log.action.toLowerCase().includes(q)) ||
          (log.tool && log.tool.toLowerCase().includes(q)) ||
          (log.reason && log.reason.toLowerCase().includes(q)) ||
          (log.result && log.result.toLowerCase().includes(q)) ||
          (log.incident_id && log.incident_id.toLowerCase().includes(q))
        );
      })
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }, [logs, filterMode, incidentFilter, searchQuery]);

  const visible = compact ? filtered.slice(0, 8) : filtered;

  const toggleExpanded = (key) =>
    setExpanded((current) => {
      const next = new Set(current);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });

  const getBadgeStyle = (log) => {
    if (log.decision === "AUTONOMOUS_RESOLVED") {
      return { bg: "rgba(35, 184, 201, 0.15)", color: "#23B8C9", border: "1px solid rgba(35, 184, 201, 0.4)", label: "🤖 AUTONOMOUS RESOLUTION" };
    }
    if (log.decision === "STOCK_CORRECTED" || log.decision === "APPROVED") {
      return { bg: "rgba(245, 158, 11, 0.15)", color: "#F59E0B", border: "1px solid rgba(245, 158, 11, 0.4)", label: "👤 HUMAN SIGN-OFF" };
    }
    if (log.tool) {
      return { bg: "rgba(139, 92, 246, 0.15)", color: "#A78BFA", border: "1px solid rgba(139, 92, 246, 0.4)", label: `🔧 ${log.tool}` };
    }
    return { bg: "rgba(255, 255, 255, 0.08)", color: "#94A3B8", border: "1px solid rgba(255, 255, 255, 0.15)", label: log.decision || "EVENT" };
  };

  return (
    <div className="panel activity-panel elevated-panel" style={{ padding: 20 }}>
      <div className="activity-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 16 }}>{title}</h3>
          <span className="activity-count" style={{ fontSize: 12, color: "#94A3B8" }}>
            {filtered.length} events logged · newest first
          </span>
        </div>

        {showFilters && (
          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
            <input
              type="text"
              placeholder="Search reasoning or tools…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                background: "rgba(0, 0, 0, 0.3)",
                border: "1px solid rgba(255, 255, 255, 0.12)",
                color: "#FFFFFF",
                padding: "5px 10px",
                borderRadius: 6,
                fontSize: 12,
              }}
            />
            {incidents.length > 0 && (
              <select
                value={incidentFilter}
                onChange={(e) => setIncidentFilter(e.target.value)}
                style={{
                  background: "rgba(0, 0, 0, 0.3)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  color: "#FFFFFF",
                  padding: "5px 10px",
                  borderRadius: 6,
                  fontSize: 12,
                }}
              >
                <option value="ALL">All Incidents</option>
                {incidents.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))}
              </select>
            )}
          </div>
        )}
      </div>

      {showFilters && (
        <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
          {Object.entries(TYPE_LABELS).map(([key, label]) => (
            <button
              key={key}
              type="button"
              onClick={() => setFilterMode(key)}
              style={{
                background: filterMode === key ? "linear-gradient(135deg, #073F46 0%, #07535A 100%)" : "rgba(255, 255, 255, 0.04)",
                color: filterMode === key ? "#23B8C9" : "#94A3B8",
                border: filterMode === key ? "1px solid rgba(35, 184, 201, 0.5)" : "1px solid rgba(255, 255, 255, 0.08)",
                padding: "6px 12px",
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {visible.length === 0 ? (
        <p className="empty-state" style={{ padding: 24, textAlign: "center", color: "#64748B" }}>
          No agent activity matches these filters.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {visible.map((log, index) => {
            const key = `${log.timestamp}-${log.incident_id}-${index}`;
            const isExpanded = expanded.has(key);
            const badge = getBadgeStyle(log);

            return (
              <div
                key={key}
                style={{
                  background: isExpanded ? "rgba(15, 23, 42, 0.85)" : "rgba(15, 23, 42, 0.5)",
                  border: isExpanded ? "1px solid rgba(35, 184, 201, 0.4)" : "1px solid rgba(255, 255, 255, 0.06)",
                  borderRadius: 8,
                  padding: 12,
                  transition: "all 0.15s ease",
                }}
              >
                <div
                  onClick={() => toggleExpanded(key)}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    cursor: "pointer",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        padding: "2px 8px",
                        borderRadius: 4,
                        background: badge.bg,
                        color: badge.color,
                        border: badge.border,
                        letterSpacing: "0.5px",
                      }}
                    >
                      {badge.label}
                    </span>

                    {log.incident_id && (
                      <Link
                        to={`/incidents/${log.incident_id}`}
                        onClick={(e) => e.stopPropagation()}
                        style={{
                          fontSize: 12,
                          fontWeight: 700,
                          color: "#23B8C9",
                          textDecoration: "none",
                        }}
                      >
                        {log.incident_id}
                      </Link>
                    )}

                    <span style={{ fontSize: 13, color: "#F1F5F9", fontWeight: 600 }}>
                      {log.action || log.decision || "Agent Event"}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 11, color: "#64748B", fontFamily: "JetBrains Mono, monospace" }}>
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span style={{ fontSize: 14, color: "#94A3B8", fontWeight: 700 }}>
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  </div>
                </div>

                {/* Reasoning & Result Preview */}
                {log.reason && !isExpanded && (
                  <div style={{ fontSize: 12, color: "#94A3B8", marginTop: 6, paddingLeft: 2 }}>
                    💡 <em>{log.reason}</em>
                  </div>
                )}

                {/* Expanded Technical Details */}
                {isExpanded && (
                  <div
                    style={{
                      marginTop: 12,
                      paddingTop: 12,
                      borderTop: "1px solid rgba(255, 255, 255, 0.08)",
                      display: "flex",
                      flexDirection: "column",
                      gap: 8,
                      fontSize: 12.5,
                    }}
                  >
                    {log.incident_id && (
                      <div>
                        <strong style={{ color: "#94A3B8" }}>Target Incident: </strong>
                        <Link to={`/incidents/${log.incident_id}`} style={{ color: "#23B8C9" }}>
                          {log.incident_id} (Open in Command Center →)
                        </Link>
                      </div>
                    )}
                    {log.tool && (
                      <div>
                        <strong style={{ color: "#A78BFA" }}>Tool Executed: </strong>
                        <code style={{ background: "rgba(0,0,0,0.4)", padding: "2px 6px", borderRadius: 4, color: "#A78BFA" }}>
                          {log.tool}
                        </code>
                      </div>
                    )}
                    {log.decision && (
                      <div>
                        <strong style={{ color: "#23B8C9" }}>Decision: </strong>
                        <span style={{ color: "#FFFFFF", fontWeight: 600 }}>{log.decision}</span>
                      </div>
                    )}
                    {log.reason && (
                      <div style={{ background: "rgba(35, 184, 201, 0.08)", padding: 10, borderRadius: 6, border: "1px solid rgba(35, 184, 201, 0.2)" }}>
                        <strong style={{ color: "#23B8C9" }}>🧠 Explainable Reasoning & Analysis: </strong>
                        <div style={{ marginTop: 4, color: "#E2E8F0", lineHeight: 1.5 }}>{log.reason}</div>
                      </div>
                    )}
                    {log.result && (
                      <div style={{ background: "rgba(0, 0, 0, 0.3)", padding: 10, borderRadius: 6 }}>
                        <strong style={{ color: "#10B981" }}>Output Payload / Tool Result: </strong>
                        <div style={{ marginTop: 4, color: "#CBD5E1", fontFamily: "JetBrains Mono, monospace", fontSize: 11.5 }}>
                          {log.result}
                        </div>
                      </div>
                    )}
                    <div style={{ fontSize: 11, color: "#64748B" }}>
                      Timestamp: {new Date(log.timestamp).toISOString()}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {compact && filtered.length > visible.length && (
        <Link
          to="/agent-activity"
          style={{
            display: "block",
            textAlign: "center",
            marginTop: 14,
            color: "#23B8C9",
            fontWeight: 600,
            fontSize: 12.5,
            textDecoration: "none",
          }}
        >
          View all {filtered.length} agent activity logs →
        </Link>
      )}
    </div>
  );
}