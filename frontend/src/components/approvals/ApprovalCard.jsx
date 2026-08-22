/**
 * src/components/approvals/ApprovalCard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * One pending human-approval decision (team doc Section 16 / spec page 4):
 * estimated cost, approval threshold, why approval is required, recommended
 * action, alternatives considered, and Approve/Reject actions.
 *
 * RECEIVES: `plan` (schemas/recovery_plan.RecoveryPlan, Dev3's contract),
 *   optional `incident` (schemas/common.IncidentOut) for context when shown
 *   outside the Incident Command Center (e.g. the standalone Approvals page).
 * DELIVERS: POST /agent/approve or /agent/reject (src/api/agent.js) via
 *   `onDecided(decision)` callback so the parent can update its own list —
 *   no business/approval logic lives here, only the request + UI state.
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { approvePlan, rejectPlan } from "../../api/agent.js";
import SeverityBadge from "../common/SeverityBadge.jsx";

export default function ApprovalCard({ plan, incident, onDecided }) {
  const [pending, setPending] = useState(null); // "approve" | "reject" | null
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
    <div className="panel" style={{ borderColor: "var(--status-high)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
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

      <div style={{ display: "flex", gap: 24, marginTop: 12, flexWrap: "wrap" }}>
        <div>
          <div className="kpi-label" style={{ fontSize: 11 }}>ESTIMATED COST</div>
          <div style={{ fontSize: 20, fontWeight: 600 }}>${recommended?.total_cost.toLocaleString()}</div>
        </div>
        <div>
          <div className="kpi-label" style={{ fontSize: 11 }}>APPROVAL THRESHOLD</div>
          <div style={{ fontSize: 20, fontWeight: 600 }}>${plan.approval_threshold_usd.toLocaleString()}</div>
        </div>
        <div>
          <div className="kpi-label" style={{ fontSize: 11 }}>DELIVERY</div>
          <div style={{ fontSize: 20, fontWeight: 600 }}>{recommended?.max_delivery_days}d</div>
        </div>
      </div>

      <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 12 }}>
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
            <div key={opt.option_id} style={{ fontSize: 12, padding: "4px 0", borderTop: "1px solid var(--border-subtle)" }}>
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
