/**
 * src/components/incidents/RecoveryPlanPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 15. Shows every option (including rejected ones with reasons)
 * plus the recommended plan and Execute/Request-Approval actions.
 *
 * RECEIVES: `plan` prop, shape = schemas/recovery_plan.RecoveryPlan (Dev3's contract)
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
      // Below the approval threshold the agent can execute directly — this reuses
      // the same /agent/approve endpoint (auto-path), matching agent_loop.py's contract.
      await approvePlan(incidentId);
      onExecuted?.();
    } catch (err) {
      setError(err.message || "Failed to execute recovery plan.");
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="panel" style={{ marginTop: 16 }}>
      <h3>Recovery Plan</h3>
      {plan.options.map((opt) => {
        const isRecommended = opt.option_id === plan.recommended_option_id;
        return (
          <div
            key={opt.option_id}
            style={{
              padding: "8px 0",
              borderBottom: "1px solid var(--border-subtle)",
              borderLeft: isRecommended ? "3px solid var(--accent)" : "3px solid transparent",
              paddingLeft: 8,
            }}
          >
            <strong>OPTION {opt.option_id}</strong>{" "}
            {isRecommended && <span className="badge badge-info">RECOMMENDED</span>}{" "}
            {opt.constraints_satisfied ? (
              <span className="badge badge-low">VALID</span>
            ) : (
              <span className="badge badge-critical">REJECTED</span>
            )}
            {opt.allocations.map((a) => (
              <div key={a.supplier_id} style={{ fontSize: 13 }}>
                {a.supplier_id} → {a.quantity} units @ ${a.unit_price}/unit, {a.delivery_days}d delivery
              </div>
            ))}
            <div style={{ fontSize: 13, color: "var(--text-secondary)" }}>
              Total: ${opt.total_cost.toLocaleString()}
              {opt.rejection_reason && <> — Reason: {opt.rejection_reason}</>}
            </div>
          </div>
        );
      })}

      <div style={{ marginTop: 12 }}>
        <strong>Recommended: Option {plan.recommended_option_id}</strong>
        <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>{plan.recommendation_reason}</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {!plan.requires_human_approval && (
        <button className="btn-primary" disabled={executing} onClick={handleExecute}>
          {executing ? "Executing…" : "▶ EXECUTE"}
        </button>
      )}
      {plan.requires_human_approval && (
        <span className="badge badge-high">HUMAN APPROVAL REQUIRED — see below</span>
      )}
    </div>
  );
}
