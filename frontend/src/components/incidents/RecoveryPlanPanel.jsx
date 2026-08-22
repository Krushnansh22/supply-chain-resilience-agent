/**
 * src/components/incidents/RecoveryPlanPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 15. Shows every option (including rejected ones with reasons)
 * plus the recommended plan and Execute/Request-Approval actions.
 *
 * RECEIVES: `plan` prop, shape = schemas/recovery_plan.RecoveryPlan (Dev3's contract)
 */
export default function RecoveryPlanPanel({ plan, incident }) {
  const recommended = plan.options.find((option) => option.option_id === plan.recommended_option_id);
  const cost = recommended?.total_cost ?? 0;
  const threshold = plan.approval_threshold_usd ?? 0;
  const approvalReason = plan.requires_human_approval
    ? `The recommended recovery costs $${cost.toLocaleString()}, which is $${(cost - threshold).toLocaleString()} above the autonomous limit of $${threshold.toLocaleString()}.`
    : `The recommended recovery costs $${cost.toLocaleString()}, within the autonomous limit of $${threshold.toLocaleString()}; the agent can execute it without waiting for a coordinator.`;
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
