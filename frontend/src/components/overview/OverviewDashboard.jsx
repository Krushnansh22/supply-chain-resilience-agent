/**
 * src/components/overview/OverviewDashboard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * First screen judges see (team doc Section 12). Composes:
 *   - Global Autonomous Agent Loop Controller (processes pending incidents sequentially)
 *   - Autonomous Anomaly & Environment Scanner
 *   - KpiCards (active/critical incidents, production-at-risk, pending approvals)
 *   - ActiveIncidentsList (clickable -> IncidentCommandCenter)
 *   - AgentActivityFeed (recent audit log entries across all incidents)
 */
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listIncidents } from "../../api/incidents.js";
import { listAuditLogs } from "../../api/audit.js";
import { listProductionOrders } from "../../api/production.js";
import { listSuppliers } from "../../api/suppliers.js";
import { scanAndTriage, processBacklog } from "../../api/agent.js";
import KpiCards from "./KpiCards.jsx";
import ActiveIncidentsList from "./ActiveIncidentsList.jsx";
import AgentActivityFeed from "./AgentActivityFeed.jsx";

export default function OverviewDashboard() {
  const [incidents, setIncidents] = useState([]);
  const [productionOrders, setProductionOrders] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [agentRunning, setAgentRunning] = useState(false);
  const [notification, setNotification] = useState(null);

  const load = useCallback(() => {
    Promise.all([listIncidents(), listAuditLogs(), listProductionOrders(), listSuppliers()])
      .then(([incidentsRes, auditRes, productionRes, suppliersRes]) => {
        setIncidents(incidentsRes);
        setAuditLogs(auditRes);
        setProductionOrders(productionRes);
        setSuppliers(suppliersRes);
      })
      .catch((err) => console.error("Overview load failed:", err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 2500);
    return () => clearInterval(interval);
  }, [load]);

  const handleStartAgentLoop = async () => {
    setAgentRunning(true);
    setNotification(null);
    try {
      // 1. First scan environment for new disruptions or corrupted stock
      await scanAndTriage();
      // 2. Then sequentially process all pending incidents in the backlog
      const res = await processBacklog();
      setNotification({
        title: "⚡ Global Agent Operations Completed",
        message: res.message || `Processed ${res.processed_count} disruptions: ${res.auto_resolved_count} auto-resolved, ${res.escalated_count} escalated for approval.`,
      });
      load();
      setTimeout(() => setNotification(null), 9000);
    } catch (err) {
      console.error("Agent execution error:", err);
      setNotification({
        title: "⚠️ Agent Operation Error",
        message: "Failed to complete autonomous queue cycle.",
      });
      setTimeout(() => setNotification(null), 5000);
    } finally {
      setAgentRunning(false);
    }
  };

  if (loading) return <p>Loading control tower…</p>;

  const waitingApprovalsCount = (incidents || []).filter((i) => i.status === "WAITING_APPROVAL").length;
  const pendingTriageCount = (incidents || []).filter((i) => i.status === "DETECTED" || i.status === "INVESTIGATING").length;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Control Tower</h1>
          <div className="page-subtitle">
            Autonomous multi-step supply chain disruption control and operations monitoring.
          </div>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={handleStartAgentLoop}
            disabled={agentRunning}
            className="btn btn-primary"
            style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 700 }}
          >
            <span>{agentRunning ? "⚙️" : "⚡"}</span>
            {agentRunning ? "Agent Processing Incidents…" : "Start Autonomous Agent"}
          </button>
          <Link to="/simulator" className="btn btn-black" style={{ textDecoration: "none" }}>
            + Inject Scenario
          </Link>
        </div>
      </div>

      {notification && (
        <div
          className="panel"
          style={{
            background: "rgba(35, 184, 201, 0.08)",
            border: "1px solid rgba(35, 184, 201, 0.4)",
            marginBottom: 20,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontWeight: 600, fontSize: 13, color: "#23B8C9", marginBottom: 2 }}>
              {notification.title}
            </div>
            <div style={{ fontSize: 12.5, color: "var(--text-secondary)" }}>
              {notification.message}
            </div>
          </div>
          {waitingApprovalsCount > 0 && (
            <Link to="/approvals" className="btn-ghost" style={{ fontSize: 12, textDecoration: "none" }}>
              View Approvals ({waitingApprovalsCount}) →
            </Link>
          )}
        </div>
      )}

      <KpiCards incidents={incidents} productionOrders={productionOrders} suppliers={suppliers} />
      <div style={{ display: "flex", gap: 16, marginTop: 24, flexWrap: "wrap" }}>
        <div style={{ flex: 2, minWidth: 320 }}>
          <ActiveIncidentsList incidents={incidents} />
        </div>
        <div style={{ flex: 1, minWidth: 260 }}>
          <AgentActivityFeed auditLogs={auditLogs} />
        </div>
      </div>
    </div>
  );
}
