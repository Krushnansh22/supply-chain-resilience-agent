/**
 * src/components/common/StatusBadge.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Maps agent/incident status values (app/agent/states.py AgentState, mirrored on
 * Incident.status) to a consistent color so a judge can read system state at a
 * glance across Overview, Incidents, and the Command Center:
 *   DETECTED -> INVESTIGATING -> SUPPLIER_CONTACT -> EVALUATING -> PLAN_READY
 *   -> WAITING_APPROVAL -> EXECUTING -> RESOLVED   (any state -> REPLANNING)
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
