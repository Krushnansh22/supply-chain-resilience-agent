import { useState } from "react";
import { Link } from "react-router-dom";
import { approvePlan, rejectPlan } from "../../api/agent.js";
import SeverityBadge from "../common/SeverityBadge.jsx";

export default function ApprovalCard({ plan, incident, onDecided }) {
  const [pending, setPending] = useState(null);
  const [error, setError] = useState(null);

  const recommended = plan?.options?.find((o) => o.option_id === plan.recommended_option_id) || plan?.options?.[0];
  const alternatives = plan?.options?.filter((o) => o.option_id !== plan.recommended_option_id) || [];

  const handleDecision = async (action) => {
    setPending(action);
    setError(null);
    try {
      if (action === "approve") await approvePlan(plan.incident_id);
      else await rejectPlan(plan.incident_id);
      onDecided?.(action);
    } catch (err) {
      setError(err.message || `Failed to ${action} plan.`);
    } finally {
      setPending(null);
    }
  };

  const costExceeded = (recommended?.total_cost ?? 0) - (plan.approval_threshold_usd ?? 50000);

  return (
    <div
      style={{
        background: "#FFFFFF",
        borderRadius: 18,
        border: "1px solid var(--border-subtle)",
        boxShadow: "0 10px 30px rgba(15, 23, 42, 0.06)",
        padding: "24px",
        marginBottom: "20px",
        transition: "all 0.2s ease",
      }}
    >
      {/* Header Row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16, flexWrap: "wrap", marginBottom: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <h3 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: "var(--text-primary)" }}>
              {incident ? (
                <Link to={`/incidents/${incident.incident_id}`} style={{ color: "var(--text-primary)", textDecoration: "none" }}>
                  {incident.incident_id}
                </Link>
              ) : (
                plan.incident_id
              )}
            </h3>
            {incident && <SeverityBadge severity={incident.severity} />}
          </div>
          {incident && (
            <div style={{ color: "var(--text-secondary)", fontSize: 13, fontWeight: 500 }}>
              {incident.type?.replaceAll("_", " ")} · Component <strong style={{ color: "var(--text-primary)" }}>{incident.affected_component}</strong> · PO <strong style={{ color: "var(--text-primary)" }}>{incident.affected_po || "—"}</strong>
            </div>
          )}
        </div>
        <span
          style={{
            background: "rgba(239, 68, 68, 0.1)",
            color: "#EF4444",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            fontSize: 11,
            fontWeight: 700,
            padding: "4px 12px",
            borderRadius: 20,
            letterSpacing: "0.05em",
          }}
        >
          APPROVAL REQUIRED
        </span>
      </div>

      {/* 3-Column Cost & SLA Metrics Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, margin: "16px 0 20px" }}>
        <div style={{ background: "#F8FAFC", borderRadius: 12, border: "1px solid var(--border-subtle)", padding: 14 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            ESTIMATED COST
          </div>
          <div style={{ fontSize: 22, fontWeight: 700, color: "var(--primary)", marginTop: 4 }}>
            ₹{recommended?.total_cost?.toLocaleString() || "0"}
          </div>
        </div>

        <div style={{ background: "#F8FAFC", borderRadius: 12, border: "1px solid var(--border-subtle)", padding: 14 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            APPROVAL THRESHOLD
          </div>
          <div style={{ fontSize: 22, fontWeight: 700, color: "var(--text-primary)", marginTop: 4 }}>
            ₹{plan.approval_threshold_usd?.toLocaleString() || "50,000"}
          </div>
        </div>

        <div style={{ background: "#F8FAFC", borderRadius: 12, border: "1px solid var(--border-subtle)", padding: 14 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            DELIVERY LEAD TIME
          </div>
          <div style={{ fontSize: 22, fontWeight: 700, color: "var(--green-accent, #10B981)", marginTop: 4 }}>
            {recommended?.max_delivery_days ?? 7} Days
          </div>
        </div>
      </div>

      {/* Why Approval is Required Notice Banner */}
      <div
        style={{
          background: "rgba(245, 158, 11, 0.08)",
          border: "1px solid rgba(245, 158, 11, 0.3)",
          borderRadius: 12,
          padding: "12px 16px",
          fontSize: 13,
          color: "#92400E",
          marginBottom: 16,
          lineHeight: 1.5,
        }}
      >
        <strong>⚠️ Why approval is required: </strong>
        This recovery plan costs ₹{recommended?.total_cost?.toLocaleString()} and exceeds the ₹{plan.approval_threshold_usd?.toLocaleString()} autonomous limit by ₹{costExceeded > 0 ? costExceeded.toLocaleString() : "0"}.
      </div>

      {/* Recommended Strategy Box */}
      <div
        style={{
          background: "#FFFFFF",
          border: "1px solid var(--border-subtle)",
          borderRadius: 12,
          padding: 16,
          marginBottom: 16,
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-primary)", marginBottom: 4 }}>
          Recommended: Option {plan.recommended_option_id}
        </div>
        <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.5 }}>
          {plan.recommendation_reason || "SUP-002 is the highest-reliability option within acceptable lead time."}
        </div>
      </div>

      {/* Alternatives Section */}
      {alternatives.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 8, letterSpacing: "0.05em" }}>
            ALTERNATIVES CONSIDERED
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {alternatives.map((opt) => (
              <div
                key={opt.option_id}
                style={{
                  display: "flex",
                  justify: "space-between",
                  alignItems: "center",
                  padding: "10px 14px",
                  background: "#F8FAFC",
                  borderRadius: 10,
                  border: "1px solid var(--border-subtle)",
                  fontSize: 13,
                }}
              >
                <div>
                  <strong style={{ color: "var(--text-primary)" }}>Option {opt.option_id}</strong> — ₹{opt.total_cost?.toLocaleString()}, {opt.max_delivery_days}d
                </div>
                {opt.constraints_satisfied ? (
                  <span style={{ background: "rgba(16,185,129,0.1)", color: "#10B981", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 6 }}>VALID</span>
                ) : (
                  <span style={{ background: "rgba(239,68,68,0.1)", color: "#EF4444", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 6 }}>
                    REJECTED: {opt.rejection_reason || "Exceeds delivery window"}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {error && <div className="error-banner" style={{ marginBottom: 14 }}>{error}</div>}

      {/* Action Buttons */}
      <div style={{ display: "flex", gap: 12, marginTop: 18 }}>
        <button
          disabled={!!pending}
          onClick={() => handleDecision("approve")}
          style={{
            background: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
            color: "#FFFFFF",
            border: "none",
            borderRadius: 10,
            padding: "10px 24px",
            fontSize: 13,
            fontWeight: 700,
            cursor: pending ? "not-allowed" : "pointer",
            boxShadow: "0 4px 12px rgba(16, 185, 129, 0.25)",
            transition: "all 0.15s ease",
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {pending === "approve" ? "Approving…" : "✓ Approve Plan"}
        </button>

        <button
          disabled={!!pending}
          onClick={() => handleDecision("reject")}
          style={{
            background: "#FFFFFF",
            color: "#EF4444",
            border: "1.5px solid #EF4444",
            borderRadius: 10,
            padding: "10px 24px",
            fontSize: 13,
            fontWeight: 700,
            cursor: pending ? "not-allowed" : "pointer",
            transition: "all 0.15s ease",
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {pending === "reject" ? "Rejecting…" : "✕ Reject Plan"}
        </button>
      </div>
    </div>
  );
}