/**
 * src/components/overview/ActiveIncidentsList.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Styled to match the reference image "Warehouse workload" panel style:
 *  - White card with panel-header (title + filter/dots icon buttons)
 *  - List of incident entries below
 *
 * RECEIVES: `incidents` prop (from GET /incidents)
 * DELIVERS: navigation to /incidents/:incidentId and /incidents
 */
import { Link } from "react-router-dom";
import StatusBadge from "../common/StatusBadge.jsx";

function timeAgo(iso) {
  if (!iso) return null;
  const diffMs = Date.now() - new Date(iso).getTime();
  const hrs = Math.floor(diffMs / 3_600_000);
  if (hrs < 1) return "just now";
  if (hrs < 24) return `${hrs} hr${hrs === 1 ? "" : "s"} ago`;
  const days = Math.floor(hrs / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}

export default function ActiveIncidentsList({ incidents }) {
  const preview = incidents.slice(0, 6);

  return (
    <div className="panel">
      {/* Panel header — matches image style */}
      <div className="panel-header">
        <span className="panel-title">Active Incidents</span>
        <div className="panel-actions">
          {incidents.length > preview.length && (
            <Link
              to="/incidents"
              className="icon-btn"
              style={{ width: "auto", padding: "4px 10px", fontSize: 11, textDecoration: "none", color: "var(--primary)" }}
            >
              View all {incidents.length} →
            </Link>
          )}
          {/* Filter icon */}
          <button className="icon-btn" title="Filter" style={{ fontSize: 14 }}>⚡</button>
          {/* More icon */}
          <button className="icon-btn" title="More options" style={{ fontSize: 16, letterSpacing: 1 }}>···</button>
        </div>
      </div>

      {/* Timeline strip */}
      <div className="mini-timeline">
        <span className="tick-label">Live &amp; recent</span>
        <div className="track" />
        <span className={`tick${preview.length ? " live" : ""}`} />
        <span className="tick-label">now</span>
      </div>

      {/* Incidents */}
      {preview.length === 0 && (
        <p className="empty-state">No active incidents. Try the Simulator.</p>
      )}
      {preview.map((incident) => (
        <Link
          key={incident.incident_id}
          to={`/incidents/${incident.incident_id}`}
          className="incident-entry"
        >
          <div className="entry-title">
            <span className="dot" />
            {incident.affected_po || incident.incident_id}
            <span style={{ fontWeight: 400, color: "var(--text-secondary)", fontSize: 11 }}>
              ({timeAgo(incident.created_at || incident.detected_at) || "recent"})
            </span>
          </div>
          <div className="entry-meta">
            Type: {incident.type?.replaceAll("_", " ")} · Component:{" "}
            {incident.affected_component}&nbsp;
            <StatusBadge status={incident.status} />
          </div>
        </Link>
      ))}
    </div>
  );
}
