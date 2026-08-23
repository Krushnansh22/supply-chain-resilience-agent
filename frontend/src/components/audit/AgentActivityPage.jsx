/**
 * src/components/audit/AgentActivityPage.jsx
 * Safe, operator-facing view of autonomous agent decisions, reasoning, and tool calls.
 */
import React, { useEffect, useState, useMemo } from "react";
import { listAuditLogs } from "../../api/audit.js";
import ActivityFeed from "./ActivityFeed.jsx";
import { useAuth } from "../../context/AuthContext.jsx";

export default function AgentActivityPage() {
  const { activeWarehouse } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const load = () =>
      listAuditLogs()
        .then((items) => {
          if (mounted) setLogs(items || []);
        })
        .catch(console.error)
        .finally(() => {
          if (mounted) setLoading(false);
        });

    load();
    const interval = setInterval(load, 2500);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [activeWarehouse]);

  // Aggregate summary metrics
  const metrics = useMemo(() => {
    let autonomousCount = 0;
    let toolCallsCount = 0;
    let humanApprovalsCount = 0;

    for (const log of logs) {
      if (log.tool) toolCallsCount++;
      if (log.decision === "AUTONOMOUS_RESOLVED" || (log.action && log.action.toLowerCase().includes("autonomous"))) {
        autonomousCount++;
      }
      if (log.decision === "STOCK_CORRECTED" || log.decision === "APPROVED") {
        humanApprovalsCount++;
      }
    }

    return {
      total: logs.length,
      autonomousCount,
      toolCallsCount,
      humanApprovalsCount,
    };
  }, [logs]);

  return (
    <div style={{ maxWidth: 1280, margin: "0 auto" }}>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <div>
          <h1>Autonomous Agent Activity & Reasoning</h1>
          <div className="page-subtitle">
            Real-time explainability stream for autonomous decisions, multi-supplier optimizations, and tool calls.
          </div>
        </div>
        <span className="badge badge-info" style={{ background: "rgba(35, 184, 201, 0.15)", color: "#23B8C9", border: "1px solid rgba(35, 184, 201, 0.4)" }}>
          LIVE TELEMETRY · 2.5S
        </span>
      </div>

      {/* KPI Stats Bar */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 14, marginBottom: 20 }}>
        <div className="panel elevated-panel" style={{ padding: 16, borderLeft: "4px solid #23B8C9" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#94A3B8", textTransform: "uppercase" }}>
            Total Audit Events
          </div>
          <div style={{ fontSize: 24, fontWeight: 800, color: "#FFFFFF", marginTop: 4 }}>
            {metrics.total}
          </div>
          <div style={{ fontSize: 11, color: "#23B8C9", marginTop: 2 }}>Immutable trace log</div>
        </div>

        <div className="panel elevated-panel" style={{ padding: 16, borderLeft: "4px solid #10B981" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#94A3B8", textTransform: "uppercase" }}>
            🤖 Autonomous Resolutions
          </div>
          <div style={{ fontSize: 24, fontWeight: 800, color: "#10B981", marginTop: 4 }}>
            {metrics.autonomousCount}
          </div>
          <div style={{ fontSize: 11, color: "#94A3B8", marginTop: 2 }}>Within $50,000 threshold</div>
        </div>

        <div className="panel elevated-panel" style={{ padding: 16, borderLeft: "4px solid #8B5CF6" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#94A3B8", textTransform: "uppercase" }}>
            🔧 Tool Calls Executed
          </div>
          <div style={{ fontSize: 24, fontWeight: 800, color: "#A78BFA", marginTop: 4 }}>
            {metrics.toolCallsCount}
          </div>
          <div style={{ fontSize: 11, color: "#94A3B8", marginTop: 2 }}>ERP, inventory & RFQs</div>
        </div>

        <div className="panel elevated-panel" style={{ padding: 16, borderLeft: "4px solid #F59E0B" }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#94A3B8", textTransform: "uppercase" }}>
            👤 Human Approvals
          </div>
          <div style={{ fontSize: 24, fontWeight: 800, color: "#F59E0B", marginTop: 4 }}>
            {metrics.humanApprovalsCount}
          </div>
          <div style={{ fontSize: 11, color: "#94A3B8", marginTop: 2 }}>Count calibrations & sign-offs</div>
        </div>
      </div>

      {loading ? (
        <p className="empty-state">Loading live agent activity…</p>
      ) : (
        <ActivityFeed logs={logs} showFilters title="Live Autonomous Reasoning & Execution Stream" />
      )}
    </div>
  );
}