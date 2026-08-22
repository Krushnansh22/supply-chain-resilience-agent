/**
 * src/components/incidents/ApprovalModal.jsx
 * Owner: Developer 4 (Frontend)
 */
import ApprovalCard from "../approvals/ApprovalCard.jsx";

export default function ApprovalModal({ plan, incidentId, onDecided }) {
  return (
    <div style={{ marginTop: 16 }}>
      <ApprovalCard plan={plan} onDecided={onDecided} />
    </div>
  );
}