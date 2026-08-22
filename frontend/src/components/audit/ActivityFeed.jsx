import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

function eventType(log) {
  if (log.tool) return "TOOL";
  if (log.decision) return "DECISION";
  if (log.action?.toLowerCase().includes("transition")) return "STATE";
  return "EVENT";
}

const TYPE_LABELS = { ALL: "All activity", DECISION: "Decisions", TOOL: "Tool calls", STATE: "State changes", EVENT: "Other events" };

export default function ActivityFeed({ logs = [], compact = false, showFilters = false, title = "Activity" }) {
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [incidentFilter, setIncidentFilter] = useState("ALL");
  const [expanded, setExpanded] = useState(() => new Set());
  const incidents = useMemo(() => [...new Set(logs.map((log) => log.incident_id).filter(Boolean))], [logs]);
  const filtered = useMemo(() => [...logs]
    .filter((log) => typeFilter === "ALL" || eventType(log) === typeFilter)
    .filter((log) => incidentFilter === "ALL" || log.incident_id === incidentFilter)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)), [logs, typeFilter, incidentFilter]);
  const visible = compact ? filtered.slice(0, 8) : filtered;
  const toggleExpanded = (key) => setExpanded((current) => {
    const next = new Set(current);
    if (next.has(key)) next.delete(key); else next.add(key);
    return next;
  });

  return (
    <div className="panel activity-panel">
      <div className="activity-heading">
        <div>
          <h3>{title}</h3>
          <span className="activity-count">{filtered.length} events · newest first</span>
        </div>
        {showFilters && <div className="activity-filters">
          <select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} aria-label="Filter activity type">
            {Object.entries(TYPE_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          {incidents.length > 0 && <select value={incidentFilter} onChange={(event) => setIncidentFilter(event.target.value)} aria-label="Filter activity incident">
            <option value="ALL">All incidents</option>
            {incidents.map((id) => <option key={id} value={id}>{id}</option>)}
          </select>}
        </div>}
      </div>
      {visible.length === 0 ? <p className="empty-state">No activity matches these filters.</p> : visible.map((log, index) => {
        const kind = eventType(log);
        const key = `${log.timestamp}-${log.incident_id}-${index}`;
        const isExpanded = expanded.has(key);
        const summary = log.decision
          ? `${log.decision.replaceAll("_", " ")} decision recorded`
          : log.tool
            ? `${log.tool.replaceAll("_", " ")} completed`
            : log.action || "Agent event recorded";
        return <div className={`activity-event${isExpanded ? " expanded" : ""}`} key={key}>
          <button className="activity-event-toggle" onClick={() => toggleExpanded(key)} aria-expanded={isExpanded}>
            <span className="activity-event-topline">
            <span className={`activity-kind activity-kind-${kind.toLowerCase()}`}>{kind}</span>
            <span className="activity-time">{new Date(log.timestamp).toLocaleString()}</span>
            {log.incident_id && <span className="activity-incident">{log.incident_id}</span>}
            <span className="activity-chevron">{isExpanded ? "−" : "+"}</span>
            </span>
            <span className="activity-action">{summary}</span>
          </button>
          {isExpanded && <div className="activity-technical">
            {log.incident_id && <div className="activity-detail"><strong>Incident:</strong> <Link to={`/incidents/${log.incident_id}`}>{log.incident_id}</Link></div>}
            <div className="activity-detail"><strong>Recorded action:</strong> {log.action || "—"}</div>
            {log.tool && <div className="activity-detail"><strong>Tool:</strong> {log.tool}</div>}
            {log.decision && <div className="activity-detail activity-decision"><strong>Decision:</strong> {log.decision}</div>}
            {log.reason && <div className="activity-detail"><strong>Reason:</strong> {log.reason}</div>}
            {log.result && <div className="activity-detail"><strong>Result:</strong> {log.result}</div>}
            <div className="activity-detail"><strong>Recorded at:</strong> {new Date(log.timestamp).toISOString()}</div>
          </div>}
        </div>;
      })}
      {compact && filtered.length > visible.length && <Link to="/agent-activity" className="activity-more">View all activity →</Link>}
    </div>
  );
}