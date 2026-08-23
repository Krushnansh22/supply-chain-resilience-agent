/**
 * src/components/incidents/RecoveryPlanPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `plan` prop, shape = schemas/recovery_plan.RecoveryPlan
 */
import { useState } from "react";
import { approvePlan } from "../../api/agent.js";

export default function RecoveryPlanPanel({ plan, incident, incidentId, onExecuted }) {
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState(null);

  if (!plan || !plan.options || plan.options.length === 0) {
    return null;
  }

  const handleExecute = async () => {
    setExecuting(true);
    setError(null);
    try {
      const targetId = incidentId || incident?.incident_id || plan.incident_id;
      await approvePlan(targetId);
      onExecuted?.();
    } catch (err) {
      setError(err.message || "Failed to execute recovery plan.");
    } finally {
      setExecuting(false);
    }
  };

  const approvalReason = plan.requires_human_approval
    ? (plan.recommendation_reason || "Estimated cost exceeds autonomous authority limits or multi-supplier trade-offs require human approval.")
    : "Recovery plan satisfies all delivery deadlines and quality constraints within autonomous spending limits.";

  return (
    <div className="panel elevated-panel" style={{ marginTop: 16 }}>
      <h3>Recovery Plan</h3>
      {(plan.options || []).map((opt) => {
        const isRecommended = opt.option_id === plan.recommended_option_id;
        return (
          <div key={opt.option_id} className={`plan-option${isRecommended ? " recommended" : ""}`}>
            <strong>OPTION {opt.option_id}</strong>{" "}
            {isRecommended && <span className="badge badge-info">RECOMMENDED</span>}{" "}
            {opt.constraints_satisfied ? (
              <span className="badge badge-low">VALID</span>
            ) : (
              <span className="badge badge-critical">REJECTED</span>
            )}
            {(opt.allocations || []).map((a, idx) => (
              <div key={a.supplier_id || idx} className="plan-option-alloc">
                {a.supplier_id} → {a.quantity} units @ ${a.unit_price}/unit, {a.delivery_days}d delivery
              </div>
            ))}
            <div className="plan-option-total">
              Total: ${(opt.total_cost ?? 0).toLocaleString()}
              {opt.rejection_reason && <> — Reason: {opt.rejection_reason}</>}
            </div>
          </div>
        );
      })}

      <div style={{ marginTop: 14 }}>
        <strong>Recommended: Option {plan.recommended_option_id || "A"}</strong>
        <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>{plan.recommendation_reason}</p>
      </div>

      <div className="decision-rationale">
        <strong>{plan.requires_human_approval ? "Why approval is required" : "Why the agent can act"}</strong>
        <p>{approvalReason}</p>
        {incident?.status && (
          <span className="activity-count">
            Current incident state: {String(incident.status).replaceAll("_", " ")}
          </span>
        )}
      </div>

      {!plan.requires_human_approval && (
        <div className="badge badge-low" style={{ marginTop: 8 }}>
          AUTONOMOUS EXECUTION — agent will apply this plan
        </div>
      )}
      {plan.requires_human_approval && (
        <span className="badge badge-high" style={{ marginTop: 8 }}>
          HUMAN APPROVAL REQUIRED — review decision brief below
        </span>
      )}

      {error && <div className="error-banner" style={{ marginTop: 10 }}>{error}</div>}
    </div>
  );
}