/**
 * src/components/common/SeverityBadge.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Single source of truth for severity -> color mapping (incident.severity from
 * schemas/common.IncidentOut: LOW | MEDIUM | HIGH | CRITICAL). Previously this
 * map was copy-pasted in several components; centralizing it here so every
 * page renders severity consistently.
 */
const SEVERITY_CLASS = {
  CRITICAL: "badge-critical",
  HIGH: "badge-high",
  MEDIUM: "badge-medium",
  LOW: "badge-low",
};

export default function SeverityBadge({ severity }) {
  if (!severity) return null;
  return <span className={`badge ${SEVERITY_CLASS[severity] || "badge-neutral"}`}>{severity}</span>;
}
