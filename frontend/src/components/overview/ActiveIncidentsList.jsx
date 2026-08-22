/**
 * src/components/overview/ActiveIncidentsList.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `incidents` prop (from GET /incidents, shape: schemas/common.IncidentOut)
 * DELIVERS: navigation to /incidents/:incidentId (Incident Command Center)
 * and /incidents (full Incidents list page)
 */
import { Link } from "react-router-dom";
import SeverityBadge from "../common/SeverityBadge.jsx";
import StatusBadge from "../common/StatusBadge.jsx";

export default function ActiveIncidentsList({ incidents }) {
  const preview = incidents.slice(0, 6);

  return (
    <div className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3>Active Incidents</h3>
        {incidents.length > preview.length && (
          <Link to="/incidents" style={{ color: "var(--accent)", fontSize: 12, textDecoration: "none" }}>
            View all {incidents.length} →
          </Link>
        )}
      </div>
      {preview.length === 0 && <p className="empty-state">No active incidents. Try the Simulator.</p>}
      {preview.map((incident) => (
        <Link key={incident.incident_id} to={`/incidents/${incident.incident_id}`} className="link-row">
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <SeverityBadge severity={incident.severity} />
            <strong>{incident.affected_po || incident.incident_id}</strong>
            <span style={{ color: "var(--text-secondary)" }}>— {incident.type.replaceAll("_", " ")}</span>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 4 }}>
            <span style={{ color: "var(--text-secondary)", fontSize: 13 }}>
              Component: {incident.affected_component}
            </span>
            <StatusBadge status={incident.status} />
          </div>
        </Link>
      ))}
    </div>
  );
}
