/**
 * src/components/incidents/RecoveryPlanPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 15. Shows every option (including rejected ones with reasons)
 * plus the recommended plan and Execute/Request-Approval actions.
 *
 * RECEIVES: `plan` prop, shape = schemas/recovery_plan.RecoveryPlan (Dev3's contract)
 */
export default function RecoveryPlanPanel({ plan, incidentId }) {
  return (
    <div className="panel" style={{ marginTop: 16 }}>
      <h3>Recovery Plan</h3>
      {plan.options.map((opt) => (
        <div key={opt.option_id} style={{ padding: "8px 0", borderBottom: "1px solid var(--border-subtle)" }}>
          <strong>OPTION {opt.option_id}</strong>{" "}
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
      ))}

      <div style={{ marginTop: 12 }}>
        <strong>Recommended: Option {plan.recommended_option_id}</strong>
        <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>{plan.recommendation_reason}</p>
      </div>

      {/* TODO (Dev4): wire EXECUTE to POST /agent/approve (auto-path) once
          agent_loop.py supports direct execution below the approval threshold. */}
      {!plan.requires_human_approval && <button>EXECUTE</button>}
      {plan.requires_human_approval && (
        <span className="badge badge-high">HUMAN APPROVAL REQUIRED</span>
      )}
    </div>
  );
}
