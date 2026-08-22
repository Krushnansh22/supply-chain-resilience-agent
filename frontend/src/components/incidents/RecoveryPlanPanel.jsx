/**
 * src/components/incidents/RecoveryPlanPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `plan` prop, shape = schemas/recovery_plan.RecoveryPlan
 */
import { useState } from "react";
import { approvePlan } from "../../api/agent.js";

export default function RecoveryPlanPanel({ plan, incidentId, onExecuted }) {
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState(null);

  const handleExecute = async () => {
    setExecuting(true);
    setError(null);
    try {
      await approvePlan(incidentId);
      onExecuted?.();
    } catch (err) {
      setError(err.message || "Failed to execute recovery plan.");
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="panel elevated-panel" style={{ marginTop: 16 }}>
      <h3>Recovery Plan</h3>
      {plan.options.map((opt) => {
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
            {opt.allocations.map((a) => (
              <div key={a.supplier_id} className="plan-option-alloc">
                {a.supplier_id} → {a.quantity} units @ ${a.unit_price}/unit, {a.delivery_days}d delivery
              </div>
            ))}
            <div className="plan-option-total">
              Total: ${opt.total_cost.toLocaleString()}
              {opt.rejection_reason && <> — Reason: {opt.rejection_reason}</>}
            </div>
          </div>
        );
      })}

      <div style={{ marginTop: 14 }}>
        <strong>Recommended: Option {plan.recommended_option_id}</strong>
        <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>{plan.recommendation_reason}</p>
      </div>

      <div className="decision-rationale">
        <strong>{plan.requires_human_approval ? "Why approval is required" : "Why the agent can act"}</strong>
        <p>{approvalReason}</p>
        {incident?.status && <span className="activity-count">Current incident state: {incident.status.replaceAll("_", " ")}</span>}
      </div>

      {!plan.requires_human_approval && (
        <div className="badge badge-low">AUTONOMOUS EXECUTION — agent will apply this plan</div>
      )}
      {plan.requires_human_approval && (
        <span className="badge badge-high">HUMAN APPROVAL REQUIRED — see below</span>
      )}
    </div>
  );
}