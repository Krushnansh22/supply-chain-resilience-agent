/**
 * src/components/incidents/ApprovalModal.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 16. Shown when RecoveryPlan.requires_human_approval is true.
 *
 * RECEIVES: `plan` prop (schemas/recovery_plan.RecoveryPlan)
 * DELIVERS: POST /agent/approve or /agent/reject (src/api/agent.js)
 */
import { approvePlan, rejectPlan } from "../../api/agent.js";

export default function ApprovalModal({ plan, incidentId }) {
  const recommended = plan.options.find((o) => o.option_id === plan.recommended_option_id);

  return (
    <div className="panel" style={{ marginTop: 16, borderColor: "var(--status-high)" }}>
      <h3>⚠️ Human Approval Required</h3>
      <p>Recovery cost: <strong>${recommended?.total_cost.toLocaleString()}</strong></p>
      <p>Autonomous limit: <strong>${plan.approval_threshold_usd.toLocaleString()}</strong></p>
      <p style={{ color: "var(--text-secondary)" }}>{plan.recommendation_reason}</p>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button onClick={() => approvePlan(incidentId).catch(console.error)}>APPROVE</button>
        <button onClick={() => rejectPlan(incidentId).catch(console.error)}>REJECT</button>
      </div>
    </div>
  );
}
