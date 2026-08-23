/**
 * src/components/common/SeverityBadge.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Single source of truth for severity -> color mapping (incident.severity from
 * schemas/common.IncidentOut: LOW | MEDIUM | HIGH | CRITICAL).
 */
const SEVERITY_CLASS = {
  CRITICAL: "badge-critical",
  HIGH: "badge-high",
  MEDIUM: "badge-medium",
  LOW: "badge-low",
};

export default function SeverityBadge({ severity }) {
  if (!severity) return null;
  return (
    <span className={`badge ${SEVERITY_CLASS[severity] || "badge-neutral"}`}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: "currentColor", display: "inline-block", opacity: 0.9 }} />
      {severity}
    </span>
  );
}