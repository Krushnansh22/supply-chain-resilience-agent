/**
 * src/components/approvals/ApprovalCard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `plan`, optional `incident`
 * DELIVERS: POST /agent/approve or /agent/reject via `onDecided(decision)`
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { approvePlan, rejectPlan } from "../../api/agent.js";
import SeverityBadge from "../common/SeverityBadge.jsx";

export default function ApprovalCard({ plan, incident, onDecided }) {
  const [pending, setPending] = useState(null);
  const [error, setError] = useState(null);

  const recommended = plan.options.find((o) => o.option_id === plan.recommended_option_id);
  const alternatives = plan.options.filter((o) => o.option_id !== plan.recommended_option_id);

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

  return (
    <div className="panel approval-glow">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, flexWrap: "wrap" }}>
        <div>
          <h3 style={{ marginBottom: 4 }}>
            {incident ? (
              <Link to={`/incidents/${incident.incident_id}`} style={{ color: "inherit", textDecoration: "none" }}>
                {incident.incident_id}
              </Link>
            ) : (
              plan.incident_id
            )}
            {incident && <span style={{ marginLeft: 8 }}><SeverityBadge severity={incident.severity} /></span>}
          </h3>
          {incident && (
            <div style={{ color: "var(--text-secondary)", fontSize: 13 }}>
              {incident.type.replaceAll("_", " ")} · Component {incident.affected_component} · PO {incident.affected_po || "—"}
            </div>
          )}
        </div>
        <span className="badge badge-high">APPROVAL REQUIRED</span>
      </div>

      <div className="approval-cost-grid">
        <div className="approval-cost-item">
          <div className="kpi-label" style={{ fontSize: 11 }}>ESTIMATED COST</div>
          <div className="kpi-value-sm">${recommended?.total_cost.toLocaleString()}</div>
        </div>
        <div className="approval-cost-item">
          <div className="kpi-label" style={{ fontSize: 11 }}>APPROVAL THRESHOLD</div>
          <div className="kpi-value-sm">${plan.approval_threshold_usd.toLocaleString()}</div>
        </div>
        <div className="approval-cost-item">
          <div className="kpi-label" style={{ fontSize: 11 }}>DELIVERY</div>
          <div className="kpi-value-sm">{recommended?.max_delivery_days}d</div>
        </div>
      </div>

      <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 14 }}>
        <strong style={{ color: "var(--text-primary)" }}>Why approval is required: </strong>
        Recommended option (${recommended?.total_cost.toLocaleString()}) exceeds the ${plan.approval_threshold_usd.toLocaleString()} autonomous-execution limit.
      </p>

      <p style={{ fontSize: 13 }}>
        <strong>Recommended: Option {plan.recommended_option_id}</strong>
        <span style={{ color: "var(--text-secondary)" }}> — {plan.recommendation_reason}</span>
      </p>

      {alternatives.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div className="kpi-label" style={{ fontSize: 11, marginBottom: 4 }}>ALTERNATIVES CONSIDERED</div>
          {alternatives.map((opt) => (
            <div key={opt.option_id} className="plan-option-alloc" style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 6, marginTop: 4 }}>
              <strong>Option {opt.option_id}</strong> — ${opt.total_cost.toLocaleString()}, {opt.max_delivery_days}d{" "}
              {opt.constraints_satisfied ? (
                <span className="badge badge-low">VALID</span>
              ) : (
                <span className="badge badge-critical">REJECTED{opt.rejection_reason ? `: ${opt.rejection_reason}` : ""}</span>
              )}
            </div>
          ))}
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <button className="btn-approve" disabled={!!pending} onClick={() => handleDecision("approve")}>
          {pending === "approve" ? "Approving…" : "✓ Approve"}
        </button>
        <button className="btn-reject" disabled={!!pending} onClick={() => handleDecision("reject")}>
          {pending === "reject" ? "Rejecting…" : "✕ Reject"}
        </button>
      </div>
    </div>
  );
}