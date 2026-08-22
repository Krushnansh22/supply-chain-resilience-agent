/**
 * src/components/incidents/ApprovalModal.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 16. Shown inline in the Incident Command Center when
 * RecoveryPlan.requires_human_approval is true. Thin wrapper around the
 * shared ApprovalCard so this view and the standalone /approvals page stay
 * in sync instead of maintaining two approve/reject implementations.
 *
 * RECEIVES: `plan` prop (schemas/recovery_plan.RecoveryPlan)
 * DELIVERS: POST /agent/approve or /agent/reject (via ApprovalCard -> src/api/agent.js)
 */
import ApprovalCard from "../approvals/ApprovalCard.jsx";

export default function ApprovalModal({ plan, incidentId, onDecided }) {
  return (
    <div style={{ marginTop: 16 }}>
      <ApprovalCard plan={plan} onDecided={onDecided} />
    </div>
  );
}
