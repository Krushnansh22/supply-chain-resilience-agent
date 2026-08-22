/**
 * src/components/overview/ActiveIncidentsList.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `incidents` prop (from GET /incidents, shape: schemas/common.IncidentOut)
 * DELIVERS: navigation to /incidents/:incidentId (Incident Command Center)
 * and /incidents (full Incidents list page)
 */
import { Link } from "react-router-dom";
import StatusBadge from "../common/StatusBadge.jsx";

function timeAgo(iso) {
  if (!iso) return null;
  const diffMs = Date.now() - new Date(iso).getTime();
  const hrs = Math.floor(diffMs / 3600000);
  if (hrs < 1) return "just now";
  if (hrs < 24) return `${hrs} hr${hrs === 1 ? "" : "s"} ago`;
  const days = Math.floor(hrs / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}

export default function ActiveIncidentsList({ incidents }) {
  const preview = incidents.slice(0, 6);

  return (
    <div className="panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3>Active Incidents</h3>
        {incidents.length > preview.length && (
          <Link to="/incidents" style={{ color: "var(--secondary)", fontSize: 12, textDecoration: "none" }}>
            View all {incidents.length} →
          </Link>
        )}
      </div>

      <div className="mini-timeline">
        <span className="tick-label">Live &amp; recent</span>
        <div className="track" />
        <span className={`tick${preview.length ? " live" : ""}`} />
        <span className="tick-label">now</span>
      </div>

      {preview.length === 0 && <p className="empty-state">No active incidents. Try the Simulator.</p>}
      {preview.map((incident) => (
        <Link key={incident.incident_id} to={`/incidents/${incident.incident_id}`} className="incident-entry">
          <div className="entry-title">
            <span className="dot" />
            {incident.affected_po || incident.incident_id}
            <span style={{ fontWeight: 400, color: "var(--text-secondary)" }}>
              ({timeAgo(incident.created_at || incident.detected_at) || "recent"})
            </span>
          </div>
          <div className="entry-meta">
            Type: {incident.type?.replaceAll("_", " ")} · Component: {incident.affected_component}{" "}
            <StatusBadge status={incident.status} />
          </div>
        </Link>
      ))}
    </div>
  );
}
