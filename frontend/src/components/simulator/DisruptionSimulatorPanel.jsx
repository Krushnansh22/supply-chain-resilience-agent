/**
 * src/components/simulator/DisruptionSimulatorPanel.jsx
 * 1-Click Disruption Simulator with Warehouse Scoping Support
 */
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { injectScenario } from "../../api/simulator.js";
import { useAuth } from "../../context/AuthContext.jsx";

const SCENARIOS = [
  {
    key: "AUTONOMOUS_RESOLVE",
    label: "Autonomous Re-route ($18,000 within threshold)",
    icon: "🤖",
    tag: "100% AUTONOMOUS RESOLUTION",
    color: "#10B981",
    description: "Minor transit delay on COMP-101. Agent automatically investigates, compares backup quotes, dispatches ERP purchase order, and resolves without stopping.",
  },
  {
    key: "NEGATIVE_STOCK",
    label: "Negative Stock Anomaly (-150 units)",
    icon: "📉",
    tag: "HUMAN VERIFICATION MANDATORY",
    color: "#EF4444",
    description: "Sets COMP-104 usable stock to -150 units. Forces agent to pause and require human manager physical count entry.",
  },
  {
    key: "MISSING_STOCK",
    label: "Missing Stock Telemetry",
    icon: "❓",
    tag: "DATA ANOMALY",
    color: "#F59E0B",
    description: "Sets COMP-102 stock record to null/missing. Triggers data integrity triage and operator count verification.",
  },
  {
    key: "SUPPLIER_DELAY",
    label: "Supplier Shipment Delay (14 Days)",
    icon: "⏱",
    tag: "OPERATIONAL DISRUPTION",
    color: "#3B82F6",
    description: "Delays PO-7712 by 14 days. Agent investigates alternative suppliers and issues emergency RFQs.",
  },
  {
    key: "SUPPLIER_LIE",
    label: "Supplier Tracking Contradiction",
    icon: "🤥",
    tag: "SUPPLIER FRAUD / LIE",
    color: "#8B5CF6",
    description: "Supplier claims shipment dispatched, but carrier tracking shows NO_PICKUP_SCAN. Agent penalizes reliability score.",
  },
  {
    key: "BUDGET_OVERRUN",
    label: "Budget Overrun (> $50,000)",
    icon: "💰",
    tag: "APPROVAL THRESHOLD",
    color: "#EC4899",
    description: "Expedited alternative supplier costs $75,000, exceeding the $50k autonomous limit and requiring coordinator sign-off.",
  },
  {
    key: "QUALITY_FAILURE",
    label: "Batch Quality Failure",
    icon: "🔬",
    tag: "QUALITY EXCLUSION",
    color: "#F97316",
    description: "Incoming shipment fails ISO9001 quality audit. Agent re-routes demand to certified backup suppliers.",
  },
  {
    key: "STALE_INVENTORY",
    label: "Stale / Expired Batch",
    icon: "📦",
    tag: "INVENTORY AUDIT",
    color: "#64748B",
    description: "Batch cycle count expired. Agent triggers warehouse quarantine and replenishment planning.",
  },
];

export default function DisruptionSimulatorPanel() {
  const { activeWarehouse, isAdmin } = useAuth();
  const [error, setError] = useState(null);
  const [injecting, setInjecting] = useState(null);
  const [lastIncident, setLastIncident] = useState(null);
  const navigate = useNavigate();

  const handleInject = async (scenario) => {
    setInjecting(scenario);
    setError(null);
    try {
      const incident = await injectScenario(scenario);
      setLastIncident(incident);
      navigate(`/incidents/${incident.incident_id}`);
    } catch (err) {
      setError(err.message || "Failed to inject scenario.");
    } finally {
      setInjecting(null);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: "0 auto" }}>
      <div className="page-header" style={{ marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1>Disruption Simulator & Data Injection</h1>
          <div className="page-subtitle">
            Inject real synthetic disruptions and data anomalies with a single click. Observe how the agent detects and isolates anomalies by warehouse.
          </div>
        </div>
        <div>
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              padding: "4px 12px",
              borderRadius: 6,
              background: "rgba(35, 184, 201, 0.15)",
              color: "#23B8C9",
              border: "1px solid rgba(35, 184, 201, 0.4)",
            }}
          >
            Target: {activeWarehouse === "ALL" ? "🌐 Global Network" : `📍 ${activeWarehouse}`}
          </span>
        </div>
      </div>

      {error && <div className="error-banner" style={{ marginBottom: 16 }}>{error}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 16 }}>
        {SCENARIOS.map((s) => (
          <div
            key={s.key}
            className="panel elevated-panel"
            style={{
              padding: 20,
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              borderTop: `3px solid ${s.color}`,
            }}
          >
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <span style={{ fontSize: 24 }}>{s.icon}</span>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    padding: "3px 8px",
                    borderRadius: "4px",
                    background: `${s.color}15`,
                    color: s.color,
                    border: `1px solid ${s.color}40`,
                    letterSpacing: "0.5px",
                  }}
                >
                  {s.tag}
                </span>
              </div>
              <h3 style={{ fontSize: 16, marginBottom: 8 }}>{s.label}</h3>
              <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5, marginBottom: 16 }}>
                {s.description}
              </p>
            </div>

            <button
              className="btn-primary"
              disabled={!!injecting}
              onClick={() => handleInject(s.key)}
              style={{
                width: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                background: `linear-gradient(135deg, ${s.color} 0%, #1E2337 150%)`,
              }}
            >
              <span>{injecting === s.key ? "Injecting into DB…" : `⚡ 1-Click Inject ${s.label}`}</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}