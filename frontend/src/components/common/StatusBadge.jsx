/**
 * src/components/common/StatusBadge.jsx
 * Owner: Developer 4 (Frontend)
 */
const STATUS_CLASS = {
  DETECTED: "badge-critical",
  INVESTIGATING: "badge-high",
  SUPPLIER_CONTACT: "badge-high",
  EVALUATING: "badge-medium",
  PLAN_READY: "badge-info",
  WAITING_APPROVAL: "badge-high",
  EXECUTING: "badge-info",
  RESOLVED: "badge-low",
  REPLANNING: "badge-medium",
};

export default function StatusBadge({ status }) {
  if (!status) return <span className="badge badge-neutral">UNKNOWN</span>;
  return (
    <span className={`badge ${STATUS_CLASS[status] || "badge-neutral"}`}>
      {status.replaceAll("_", " ")}
    </span>
  );
}