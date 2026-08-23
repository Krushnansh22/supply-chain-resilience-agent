/**
 * src/components/incidents/IncidentCommandCenter.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: incidentId from the route
 * DELIVERS: POST /agent/trigger, /agent/approve, /agent/reject via user actions
 *           and comprehensive LLM operations report viewing + PDF download.
 */
import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getIncident, getIncidentActivity, getIncidentReport } from "../../api/incidents.js";
import { getAgentState, getAgentPlan, triggerAgent } from "../../api/agent.js";

import SeverityBadge from "../common/SeverityBadge.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import InfoCards from "./InfoCards.jsx";
import RecoveryPlanPanel from "./RecoveryPlanPanel.jsx";
import ApprovalModal from "./ApprovalModal.jsx";
import AgentThoughtStream from "./AgentThoughtStream.jsx";
import { downloadOperatorReport } from "../../api/reports.js";

const FLOW_STEPS = [
  { key: "DETECTED", label: "Disruption" },
  { key: "INVESTIGATING", label: "Investigation" },
  { key: "SUPPLIER_CONTACT", label: "Agent Actions" },
  { key: "EVALUATING", label: "Recovery Options" },
  { key: "PLAN_READY", label: "Decision" },
  { key: "WAITING_APPROVAL", label: "Approval" },
  { key: "EXECUTING", label: "ERP Update" },
  { key: "RESOLVED", label: "Audit" },
];
const FLOW_ORDER = FLOW_STEPS.map((s) => s.key);

export default function IncidentCommandCenter() {
  const { incidentId } = useParams();
  const [incident, setIncident] = useState(null);
  const [agentState, setAgentState] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [plan, setPlan] = useState(null);
  const [triggerError, setTriggerError] = useState(null);
  const [triggering, setTriggering] = useState(false);
  const [reporting, setReporting] = useState(false);

  // AI Brief Report State
  const [showAiReport, setShowAiReport] = useState(false);
  const [aiReportData, setAiReportData] = useState(null);
  const [aiReportLoading, setAiReportLoading] = useState(false);

  const refresh = useCallback(() => {
    getIncident(incidentId).then(setIncident).catch(console.error);
    getAgentState(incidentId).then((r) => setAgentState(r.state)).catch(console.error);
    getIncidentActivity(incidentId).then(setAuditLogs).catch(console.error);
    getAgentPlan(incidentId).then(setPlan).catch(() => setPlan(null));
  }, [incidentId]);

  useEffect(() => {
    refresh();
    const interval = setInterval(() => {
      if (agentState !== "RESOLVED") refresh();
    }, 2000);
    return () => clearInterval(interval);
  }, [refresh, agentState]);

  const handleTrigger = async () => {
    setTriggering(true);
    setTriggerError(null);
    try {
      await triggerAgent(incidentId);
      refresh();
    } catch (err) {
      setTriggerError(err.message || "Failed to trigger agent.");
    } finally {
      setTriggering(false);
    }
  };

  const handleReport = async () => {
    setReporting(true);
    try {
      await downloadOperatorReport({ incidentId });
    } catch (err) {
      setTriggerError(err.message || "Failed to generate report.");
    } finally {
      setReporting(false);
    }
  };

  const handleToggleAiReport = async () => {
    if (!showAiReport && !aiReportData) {
      setAiReportLoading(true);
      try {
        const data = await getIncidentReport(incidentId);
        setAiReportData(data);
      } catch (err) {
        console.error("Failed to load incident report:", err);
      } finally {
        setAiReportLoading(false);
      }
    }
    setShowAiReport(!showAiReport);
  };

  if (!incident) {
    return (
      <div className="loading-shell">
        <span className="loading-orb" />
        <span>Loading incident…</span>
      </div>
    );
  }

  const currentStepIndex = FLOW_ORDER.indexOf(agentState);

  return (
    <div>
      <div className="panel elevated-panel">
        <div className="command-header">
          <div>
            <h2>{incident.affected_po || incident.incident_id} — {incident.type.replaceAll("_", " ")}</h2>
            <div className="command-meta">
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={agentState || incident.status} />
              <span className="command-id">{incident.incident_id}</span>
            </div>
          </div>
          <div className="command-actions">
            <button
              className="btn-ghost"
              disabled={aiReportLoading}
              onClick={handleToggleAiReport}
              style={{ display: "flex", alignItems: "center", gap: 6 }}
            >
              {aiReportLoading ? "Analyzing…" : (showAiReport ? "Hide AI Brief" : "👁 AI Incident Brief")}
            </button>
            <button className="btn-ghost" disabled={reporting} onClick={handleReport}>
              {reporting ? "Preparing…" : "↓ Download PDF"}
            </button>
            {agentState === "WAITING_APPROVAL" ? (
              <a href="/approvals" className="btn btn-primary" style={{ textDecoration: "none", display: "inline-flex", alignItems: "center" }}>
                ⚠️ Review Escalation
              </a>
            ) : agentState === "RESOLVED" ? (
              <button className="btn-ghost" disabled={triggering} onClick={handleTrigger} title="Re-evaluate with fresh context">
                {triggering ? "Re-evaluating…" : "🔄 Re-run Analysis"}
              </button>
            ) : (
              <button className="btn-primary" disabled={triggering} onClick={handleTrigger}>
                {triggering ? "Agent Reasoning…" : "⚡ Run Agent Loop"}
              </button>
            )}
          </div>
        </div>

        <div className="flow-strip">
          {FLOW_STEPS.map((step, i) => (
            <span key={step.key} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span className={`flow-step${i <= currentStepIndex ? " active" : ""}`}>{step.label}</span>
              {i < FLOW_STEPS.length - 1 && <span className="flow-sep">→</span>}
            </span>
          ))}
        </div>

        {triggerError && <div className="error-banner">{triggerError}</div>}
      </div>

      {/* AI Incident Executive Brief Panel */}
      {showAiReport && aiReportData && (
        <div className="panel elevated-panel" style={{ marginTop: 16, borderColor: "rgba(49, 87, 213, 0.4)", background: "rgba(49, 87, 213, 0.03)", padding: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, borderBottom: "1px solid var(--border-subtle)", paddingBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span className="badge badge-primary">AI EXECUTIVE BRIEF</span>
              <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
                Comprehensive Operations Analysis — {incident.incident_id}
              </span>
            </div>
            <button className="btn-ghost" style={{ fontSize: 12 }} onClick={handleReport} disabled={reporting}>
              {reporting ? "Downloading…" : "↓ Download Formatted PDF"}
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--primary)", textTransform: "uppercase", marginBottom: 4 }}>
                Executive Summary
              </div>
              <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: "var(--text-secondary)" }}>
                {aiReportData.narrative?.executive_summary}
              </p>
            </div>

            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--primary)", textTransform: "uppercase", marginBottom: 4 }}>
                Supply Chain Impact & Stockout Risk
              </div>
              <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: "var(--text-secondary)" }}>
                {aiReportData.narrative?.impact_assessment}
              </p>
            </div>

            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--primary)", textTransform: "uppercase", marginBottom: 4 }}>
                Decision Rationale & Governance
              </div>
              <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: "var(--text-secondary)" }}>
                {aiReportData.narrative?.recovery_strategy}
              </p>
            </div>

            {aiReportData.narrative?.action_items && aiReportData.narrative.action_items.length > 0 && (
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--primary)", textTransform: "uppercase", marginBottom: 4 }}>
                  Actionable Directives
                </div>
                <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6 }}>
                  {aiReportData.narrative.action_items.map((act, idx) => (
                    <li key={idx} style={{ marginBottom: 2 }}>{act}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Autonomous Resolution & Decision Brief Banner */}
      {incident.status === "RESOLVED" && (
        <div
          className="panel elevated-panel"
          style={{
            marginTop: 16,
            marginBottom: 16,
            background: incident.resolution_mode === "AUTONOMOUS" ? "rgba(16, 185, 129, 0.06)" : "rgba(245, 158, 11, 0.06)",
            border: incident.resolution_mode === "AUTONOMOUS" ? "1px solid rgba(16, 185, 129, 0.4)" : "1px solid rgba(245, 158, 11, 0.4)",
            borderLeft: incident.resolution_mode === "AUTONOMOUS" ? "5px solid #10B981" : "5px solid #F59E0B",
            padding: 20,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span
                style={{
                  fontSize: 11,
                  fontWeight: 800,
                  padding: "3px 10px",
                  borderRadius: 6,
                  background: incident.resolution_mode === "AUTONOMOUS" ? "#10B98120" : "#F59E0B20",
                  color: incident.resolution_mode === "AUTONOMOUS" ? "#10B981" : "#F59E0B",
                  border: incident.resolution_mode === "AUTONOMOUS" ? "1px solid #10B98160" : "1px solid #F59E0B60",
                  letterSpacing: "0.5px",
                }}
              >
                {incident.resolution_mode === "AUTONOMOUS" ? "🤖 AUTONOMOUSLY RESOLVED BY AGENT" : "👤 HUMAN VERIFIED & APPROVED"}
              </span>
              <span style={{ fontSize: 13, color: "#94A3B8" }}>
                Resolved by: <strong style={{ color: "#FFFFFF" }}>{incident.resolved_by || (incident.resolution_mode === "AUTONOMOUS" ? "Autonomous Agent" : "Coordinator")}</strong>
              </span>
            </div>
            {incident.resolved_at && (
              <span style={{ fontSize: 11, color: "#64748B", fontFamily: "JetBrains Mono, monospace" }}>
                Resolved: {new Date(incident.resolved_at).toLocaleString()}
              </span>
            )}
          </div>

          <div style={{ fontSize: 14, fontWeight: 700, color: "#FFFFFF", marginBottom: 6 }}>
            🧠 Decision Rationale & Governance Trace:
          </div>
          <p style={{ margin: 0, fontSize: 13.5, color: "#E2E8F0", lineHeight: 1.6 }}>
            {incident.autonomous_reasoning || plan?.recommendation_reason || "Incident evaluated and resolved according to policy constraints."}
          </p>

          <div style={{ display: "flex", gap: 10, marginTop: 14, flexWrap: "wrap" }}>
            <span style={{ fontSize: 11, fontWeight: 600, padding: "3px 8px", borderRadius: 4, background: "rgba(255,255,255,0.06)", color: "#CBD5E1" }}>
              ✓ Autonomous Threshold: &le; $50,000
            </span>
            <span style={{ fontSize: 11, fontWeight: 600, padding: "3px 8px", borderRadius: 4, background: "rgba(255,255,255,0.06)", color: "#CBD5E1" }}>
              ✓ SLA Compliance: Delivery Met
            </span>
            <span style={{ fontSize: 11, fontWeight: 600, padding: "3px 8px", borderRadius: 4, background: "rgba(255,255,255,0.06)", color: "#CBD5E1" }}>
              ✓ Audit Logged: Immutable Trace
            </span>
          </div>
        </div>
      )}

      <InfoCards incident={incident} plan={plan} />

      {/* Autonomous Multi-Step Reasoning & Thought Stream Visualizer */}
      <AgentThoughtStream
        auditLogs={auditLogs}
        isRunning={triggering || agentState === "INVESTIGATING" || agentState === "REPLANNING"}
        incidentStatus={agentState || incident.status}
      />

      {plan && <RecoveryPlanPanel plan={plan} incident={incident} />}

      {agentState === "WAITING_APPROVAL" && plan && (
        <ApprovalModal plan={plan} incidentId={incidentId} onDecided={refresh} />
      )}
    </div>
  );
}