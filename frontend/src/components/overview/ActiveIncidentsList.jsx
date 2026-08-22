/**
 * src/components/overview/ActiveIncidentsList.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `incidents` prop (from GET /incidents, shape: schemas/common.IncidentOut)
 * DELIVERS: navigation to /incidents/:incidentId (Incident Command Center)
 */
import { Link } from "react-router-dom";

const SEVERITY_CLASS = {
  CRITICAL: "badge-critical",
  HIGH: "badge-high",
  MEDIUM: "badge-medium",
  LOW: "badge-low",
};

export default function ActiveIncidentsList({ incidents }) {
  return (
    <div className="panel">
      <h3>Active Incidents</h3>
      {incidents.length === 0 && <p style={{ color: "var(--text-muted)" }}>No active incidents. Try the Simulator.</p>}
      {incidents.map((incident) => (
        <Link
          key={incident.incident_id}
          to={`/incidents/${incident.incident_id}`}
          style={{ display: "block", padding: "8px 0", borderBottom: "1px solid var(--border-subtle)", textDecoration: "none", color: "inherit" }}
        >
          <span className={`badge ${SEVERITY_CLASS[incident.severity] || ""}`}>{incident.severity}</span>{" "}
          <strong>{incident.affected_po || incident.incident_id}</strong> — {incident.type.replaceAll("_", " ")}
          <div style={{ color: "var(--text-secondary)", fontSize: 13 }}>
            Component: {incident.affected_component} · Agent status: {incident.status}
          </div>
        </Link>
      ))}
    </div>
  );
}
