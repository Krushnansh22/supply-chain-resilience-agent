/**
 * src/components/incidents/IncidentsListPage.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: GET /incidents, GET /production
 * DELIVERS: navigation to /incidents/:incidentId
 */
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { listIncidents } from "../../api/incidents.js";
import { listProductionOrders } from "../../api/production.js";
import SeverityBadge from "../common/SeverityBadge.jsx";
import StatusBadge from "../common/StatusBadge.jsx";

const SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export default function IncidentsListPage() {
  const [incidents, setIncidents] = useState([]);
  const [productions, setProductions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState("ALL");

  useEffect(() => {
    Promise.all([
      listIncidents("all").catch(() => []),
      listProductionOrders().catch(() => [])
    ])
      .then(([incidentsRes, productionsRes]) => {
        setIncidents(Array.isArray(incidentsRes) ? incidentsRes : []);
        setProductions(Array.isArray(productionsRes) ? productionsRes : []);
        setError(null);
      })
      .catch((err) => {
        console.error("Incidents list load failed:", err);
        setError("Failed to load incidents list.");
      })
      .finally(() => setLoading(false));
  }, []);

  const productionByComponent = useMemo(() => {
    const map = {};
    for (const p of productions) {
      if (!map[p.component_id]) map[p.component_id] = [];
      map[p.component_id].push(p);
    }
    return map;
  }, [productions]);

  const filtered = useMemo(
    () => (severityFilter === "ALL" ? incidents : incidents.filter((i) => i.severity === severityFilter)),
    [incidents, severityFilter]
  );

  if (loading) {
    return (
      <div className="loading-shell">
        <span className="loading-orb" />
        <span>Loading incidents…</span>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Incidents</h1>
          <div className="page-subtitle">{incidents.length} total · {filtered.length} shown</div>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {["ALL", ...SEVERITY_ORDER].map((s) => (
            <button
              key={s}
              className={`pill-filter${severityFilter === s ? " active" : ""}`}
              onClick={() => setSeverityFilter(s)}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="panel elevated-panel">
        {filtered.length === 0 ? (
          <p className="empty-state">No incidents match this filter.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Incident</th>
                <th>Component</th>
                <th>Purchase Order</th>
                <th>Production Impact</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((incident) => {
                const affected = productionByComponent[incident.affected_component] || [];
                return (
                  <tr key={incident.incident_id}>
                    <td><SeverityBadge severity={incident.severity} /></td>
                    <td>
                      <Link to={`/incidents/${incident.incident_id}`} style={{ color: "var(--accent-2)", textDecoration: "none", fontWeight: 600 }}>
                        {incident.incident_id}
                      </Link>
                      <div style={{ color: "var(--text-secondary)", fontSize: 12 }}>
                        {incident.type.replaceAll("_", " ")}
                      </div>
                    </td>
                    <td>{incident.affected_component || "—"}</td>
                    <td>{incident.affected_po || "—"}</td>
                    <td>
                      {affected.length === 0
                        ? "—"
                        : affected.map((p) => (
                            <div key={p.production_id} style={{ fontSize: 12 }}>
                              {p.production_id} · {p.product} ({p.priority})
                            </div>
                          ))}
                    </td>
                    <td><StatusBadge status={incident.status} /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}