/**
 * src/components/layout/AgentControlRibbon.jsx
 *
 * Global Autonomous Agent Control Ribbon:
 * - Start / Stop Agent Controller
 * - Live step-by-step resolution status & ticker
 * - 1-Click Disruption injection bar (including Negative Stock and Missing Stock)
 * - Environment scan trigger
 */

import React, { useEffect, useState, useCallback } from "react";
import { startAgent, stopAgent, getAgentStatus, scanEnvironment } from "../../api/agent.js";
import { injectScenario } from "../../api/simulator.js";
import { useNavigate } from "react-router-dom";

export default function AgentControlRibbon() {
  const [statusData, setStatusData] = useState({
    is_running: false,
    status: "STOPPED",
    current_incident_id: null,
    current_step: "IDLE",
    message: "Agent is offline.",
    queue_length: 0,
    stats: { total: 0, resolved: 0, waiting_approval: 0, in_progress: 0 },
  });
  const [loadingAction, setLoadingAction] = useState(false);
  const [injecting, setInjecting] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);
  const navigate = useNavigate();

  const fetchStatus = useCallback(() => {
    getAgentStatus()
      .then((res) => {
        if (res) {
          setStatusData(res);
          window.dispatchEvent(new CustomEvent("scda_agent_activity_updated"));
        }
      })
      .catch((err) => console.error("Failed to fetch agent status:", err));
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(() => {
      if (document.visibilityState === "visible") {
        fetchStatus();
      }
    }, statusData.is_running ? 2500 : 6000);
    return () => clearInterval(interval);
  }, [fetchStatus, statusData.is_running]);

  const handleToggleAgent = async () => {
    setLoadingAction(true);
    try {
      if (statusData.is_running) {
        const res = await stopAgent();
        showToast("Agent stopped by operator.");
        fetchStatus();
      } else {
        const res = await startAgent();
        showToast("Agent started! Environment scan initiated.");
        fetchStatus();
      }
      window.dispatchEvent(new CustomEvent("scda_agent_activity_updated"));
    } catch (err) {
      showToast(err.message || "Failed to update agent state.", true);
    } finally {
      setLoadingAction(false);
    }
  };

  const handleScan = async () => {
    setLoadingAction(true);
    try {
      const res = await scanEnvironment();
      showToast(`Environment scanned: ${res.scanned_count} incident(s) detected.`);
      fetchStatus();
      window.dispatchEvent(new CustomEvent("scda_agent_activity_updated"));
    } catch (err) {
      showToast(err.message || "Scan failed.", true);
    } finally {
      setLoadingAction(false);
    }
  };

  const handleQuickInject = async (scenarioKey, label) => {
    setInjecting(scenarioKey);
    try {
      const inc = await injectScenario(scenarioKey);
      showToast(`⚡ Injected ${label} (${inc.incident_id})!`);
      fetchStatus();
      window.dispatchEvent(new CustomEvent("scda_agent_activity_updated"));
    } catch (err) {
      showToast(err.message || "Disruption injection failed.", true);
    } finally {
      setInjecting(null);
    }
  };

  const showToast = (msg, isError = false) => {
    setToastMessage({ text: msg, isError });
    setTimeout(() => setToastMessage(null), 3500);
  };

  const isRunning = statusData.is_running;

  return (
    <div
      style={{
        background: isRunning
          ? "linear-gradient(90deg, rgba(16, 185, 129, 0.12) 0%, rgba(30, 35, 55, 0.95) 100%)"
          : "rgba(26, 34, 52, 0.85)",
        borderBottom: isRunning ? "1px solid rgba(16, 185, 129, 0.4)" : "1px solid rgba(255, 255, 255, 0.08)",
        backdropFilter: "blur(12px)",
        padding: "10px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 16,
        flexWrap: "wrap",
        fontSize: 13,
        zIndex: 40,
        transition: "all 0.3s ease",
      }}
    >
      {/* Left: Start / Stop Button & Status Beacon */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <button
          onClick={handleToggleAgent}
          disabled={loadingAction}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "7px 16px",
            borderRadius: "6px",
            fontWeight: 700,
            fontSize: 13,
            cursor: "pointer",
            border: "none",
            background: isRunning
              ? "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)"
              : "linear-gradient(135deg, #10B981 0%, #059669 100%)",
            color: "#FFFFFF",
            boxShadow: isRunning
              ? "0 0 14px rgba(239, 68, 68, 0.4)"
              : "0 0 14px rgba(16, 185, 129, 0.4)",
            transition: "all 0.2s ease",
          }}
        >
          {loadingAction ? (
            <span>Connecting…</span>
          ) : isRunning ? (
            <>
              <span style={{ fontSize: 11 }}>⏹</span> Stop Autonomous Agent
            </>
          ) : (
            <>
              <span style={{ fontSize: 11 }}>▶</span> Start Autonomous Agent
            </>
          )}
        </button>

        {/* Status Indicator */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              backgroundColor: isRunning ? "#10B981" : "#6B7280",
              boxShadow: isRunning ? "0 0 10px #10B981" : "none",
              animation: isRunning ? "pulse 1.8s infinite" : "none",
            }}
          />
          <span style={{ fontWeight: 600, color: isRunning ? "#10B981" : "var(--text-secondary)" }}>
            {isRunning ? "Agent Running" : "Agent Standby"}
          </span>
        </div>

        {/* Live Step / Message */}
        <div
          style={{
            padding: "4px 12px",
            background: "rgba(255, 255, 255, 0.04)",
            borderRadius: "4px",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            color: isRunning ? "var(--text-primary)" : "var(--text-secondary)",
            maxWidth: 450,
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
          title={statusData.message}
        >
          {statusData.current_incident_id ? (
            <span>
              <strong style={{ color: "var(--primary, #00C6FF)" }}>{statusData.current_incident_id}</strong>:{" "}
              {statusData.message}
            </span>
          ) : (
            <span>{statusData.message}</span>
          )}
        </div>
      </div>

      {/* Right: Quick 1-Click Disruption Injections & Scanner */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
          ⚡ 1-Click Disrupt:
        </span>

        <button
          className="btn-ghost"
          style={{
            fontSize: 11.5,
            padding: "4px 10px",
            borderColor: "rgba(239, 68, 68, 0.4)",
            color: "#EF4444",
            background: "rgba(239, 68, 68, 0.08)",
            fontWeight: 600,
          }}
          disabled={!!injecting}
          onClick={() => handleQuickInject("NEGATIVE_STOCK", "Negative Stock (-150 units)")}
          title="Inject negative stock on COMP-104 (Mandates Human Count Verification)"
        >
          {injecting === "NEGATIVE_STOCK" ? "Injecting…" : "📉 -Stock Anomaly"}
        </button>

        <button
          className="btn-ghost"
          style={{
            fontSize: 11.5,
            padding: "4px 10px",
            borderColor: "rgba(245, 158, 11, 0.4)",
            color: "#F59E0B",
            background: "rgba(245, 158, 11, 0.08)",
            fontWeight: 600,
          }}
          disabled={!!injecting}
          onClick={() => handleQuickInject("MISSING_STOCK", "Missing Stock Record")}
          title="Inject missing/null stock data on COMP-102"
        >
          {injecting === "MISSING_STOCK" ? "Injecting…" : "❓ Missing Stock"}
        </button>

        <button
          className="btn-ghost"
          style={{ fontSize: 11.5, padding: "4px 10px" }}
          disabled={!!injecting}
          onClick={() => handleQuickInject("SUPPLIER_DELAY", "Supplier Delay")}
        >
          {injecting === "SUPPLIER_DELAY" ? "Injecting…" : "⏱ Delay"}
        </button>

        <button
          className="btn-ghost"
          style={{ fontSize: 11.5, padding: "4px 10px" }}
          disabled={!!injecting}
          onClick={() => handleQuickInject("SUPPLIER_LIE", "Supplier Lie")}
        >
          {injecting === "SUPPLIER_LIE" ? "Injecting…" : "🤥 Supplier Lie"}
        </button>

        <button
          className="btn-ghost"
          style={{ fontSize: 11.5, padding: "4px 10px" }}
          disabled={!!injecting}
          onClick={() => handleQuickInject("BUDGET_OVERRUN", "Budget Overrun")}
          title="Alternative cost > $50,000 threshold"
        >
          {injecting === "BUDGET_OVERRUN" ? "Injecting…" : "💰 >$50k Approval"}
        </button>

        <button
          className="btn-ghost"
          style={{ fontSize: 11.5, padding: "4px 10px", color: "var(--primary)" }}
          onClick={handleScan}
          disabled={loadingAction}
          title="Run complete database scan for disruptions"
        >
          🔄 Rescan DB
        </button>
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: "fixed",
            bottom: 24,
            right: 24,
            background: toastMessage.isError ? "rgba(239, 68, 68, 0.95)" : "rgba(16, 185, 129, 0.95)",
            color: "#FFFFFF",
            padding: "10px 18px",
            borderRadius: "6px",
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
            fontSize: 13,
            fontWeight: 600,
            zIndex: 9999,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <span>{toastMessage.isError ? "✕" : "✓"}</span>
          <span>{toastMessage.text}</span>
        </div>
      )}
    </div>
  );
}
