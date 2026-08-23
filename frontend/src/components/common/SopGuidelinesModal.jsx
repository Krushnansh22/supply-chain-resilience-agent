import { useState } from "react";

export default function SopGuidelinesModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState("overview");

  if (!isOpen) return null;

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      background: "rgba(15, 23, 42, 0.5)", backdropFilter: "blur(6px)",
      display: "flex", alignItems: "center", justifyContent: "center",
      zIndex: 10000, padding: 20,
    }}>
      <div style={{
        background: "#FFFFFF", borderRadius: 20, width: 740, maxWidth: "100%",
        maxHeight: "90vh", overflow: "hidden", display: "flex", flexDirection: "column",
        boxShadow: "0 25px 60px rgba(0,0,0,0.25)", border: "1px solid var(--border-subtle)",
      }}>
        {/* Header */}
        <div style={{
          padding: "20px 24px", borderBottom: "1px solid var(--border-subtle)",
          display: "flex", justifyContent: "space-between", alignItems: "center",
          background: "linear-gradient(135deg, #1E2337 0%, #0F172A 100%)", color: "#FFFFFF",
        }}>
          <div>
            <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.08em", color: "#00C6FF", textTransform: "uppercase" }}>
              Control Tower SOP & Guidelines
            </span>
            <h2 style={{ margin: "4px 0 0", fontSize: 18, color: "#FFFFFF" }}>
              Standard Operating Procedures & Resilience Policies
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "rgba(255,255,255,0.1)", border: "none", color: "#FFFFFF",
              borderRadius: "50%", width: 32, height: 32, fontSize: 16, cursor: "pointer",
            }}
          >
            ✕
          </button>
        </div>

        {/* Navigation Tabs */}
        <div style={{ display: "flex", borderBottom: "1px solid var(--border-subtle)", background: "#F8FAFC" }}>
          {[
            { id: "overview", label: "📋 Executive SOP" },
            { id: "governance", label: "⚖️ Financial Limits (₹50k)" },
            { id: "incidents", label: "🚨 Incident Response SLAs" },
            { id: "filtering", label: "🔍 Search & Sorting Tips" },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1, padding: "12px 16px", border: "none", background: "none",
                fontSize: 13, fontWeight: 600, cursor: "pointer",
                color: activeTab === tab.id ? "var(--primary)" : "var(--text-secondary)",
                borderBottom: activeTab === tab.id ? "2px solid var(--primary)" : "2px solid transparent",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Body Content */}
        <div style={{ padding: 24, overflowY: "auto", flex: 1, fontSize: 13, lineHeight: 1.6, color: "var(--text-primary)" }}>
          {activeTab === "overview" && (
            <div>
              <h3 style={{ margin: "0 0 10px", fontSize: 15, color: "var(--primary)" }}>Control Tower Governance Overview</h3>
              <p>
                The Supply Chain Resilience Platform operates an autonomous AI decision agent paired with human-in-the-loop oversight. All operational events across inventory breaches, supplier delays, and production line holds follow established Standard Operating Procedures (SOP).
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 16 }}>
                <div style={{ padding: 14, background: "#F1F5F9", borderRadius: 10, borderLeft: "4px solid #2563EB" }}>
                  <strong style={{ display: "block", marginBottom: 4, color: "#2563EB" }}>🤖 Autonomous Mode</strong>
                  Plans under ₹50,000 are automatically executed by the decision engine to maintain zero-downtime production throughput.
                </div>
                <div style={{ padding: 14, background: "#FEF3C7", borderRadius: 10, borderLeft: "4px solid #F59E0B" }}>
                  <strong style={{ display: "block", marginBottom: 4, color: "#D97706" }}>👤 Human Oversight</strong>
                  Recovery plans exceeding ₹50,000 or split multi-supplier allocations require explicit operator authorization.
                </div>
              </div>
            </div>
          )}

          {activeTab === "governance" && (
            <div>
              <h3 style={{ margin: "0 0 10px", fontSize: 15, color: "var(--primary)" }}>Financial Authorization Thresholds</h3>
              <ul style={{ paddingLeft: 20, margin: 0 }}>
                <li><strong>Tier 1 (&lt; ₹50,000):</strong> Autonomous PO dispatch to backup suppliers with stock safety buffer.</li>
                <li><strong>Tier 2 (₹50,000 - ₹200,000):</strong> Requires Operations Manager sign-off via the Approvals Dashboard.</li>
                <li><strong>Tier 3 (&gt; ₹200,000):</strong> Requires Director review + secondary logistics buffer verification.</li>
              </ul>
              <div style={{ marginTop: 16, padding: 12, background: "#EFF6FF", borderRadius: 8, color: "#1D4ED8" }}>
                💡 <em>Note: All amounts in this Control Tower are denominated in Indian Rupees (₹).</em>
              </div>
            </div>
          )}

          {activeTab === "incidents" && (
            <div>
              <h3 style={{ margin: "0 0 10px", fontSize: 15, color: "var(--primary)" }}>Target Incident SLA Standards</h3>
              <table className="custom-data-table" style={{ marginTop: 10 }}>
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>Response Window</th>
                    <th>Target Resolution</th>
                    <th>Action Protocol</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span className="badge badge-critical">CRITICAL</span></td>
                    <td>&lt; 5 minutes</td>
                    <td>&lt; 2 hours</td>
                    <td>Instant dual-vendor allocation & buffer reroute</td>
                  </tr>
                  <tr>
                    <td><span className="badge badge-high">HIGH</span></td>
                    <td>&lt; 15 minutes</td>
                    <td>&lt; 6 hours</td>
                    <td>Expedited delivery request to primary supplier</td>
                  </tr>
                  <tr>
                    <td><span className="badge badge-medium">MEDIUM</span></td>
                    <td>&lt; 1 hour</td>
                    <td>&lt; 24 hours</td>
                    <td>Buffer inventory check & batch re-order</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {activeTab === "filtering" && (
            <div>
              <h3 style={{ margin: "0 0 10px", fontSize: 15, color: "var(--primary)" }}>Advanced Search, Filtering & Column Sorting</h3>
              <p style={{ marginBottom: 12 }}>
                Use table controls for maximum efficiency across Incidents, Inventory, Production, Suppliers, and Reports:
              </p>
              <ul style={{ paddingLeft: 20, margin: 0 }}>
                <li><strong>Column Header Sorting:</strong> Click any table column header to toggle ascending (▲) or descending (▼) sort order.</li>
                <li><strong>Multi-Field Search:</strong> Filter across PO Numbers, Component SKUs, Supplier names, and Status flags simultaneously.</li>
                <li><strong>Date Restriction Guardrail:</strong> Reports and date filters strictly disallow future date selection (`max = today`).</li>
                <li><strong>Targeted PDF Download:</strong> Filter PDF compilation by specific Order ID or Supplier vendor dropdowns.</li>
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ padding: "16px 24px", borderTop: "1px solid var(--border-subtle)", textAlign: "right", background: "#F8FAFC" }}>
          <button className="btn-primary" onClick={onClose}>
            Got It
          </button>
        </div>
      </div>
    </div>
  );
}
