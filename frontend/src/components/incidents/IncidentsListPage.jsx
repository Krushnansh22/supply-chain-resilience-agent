/**
 * src/components/incidents/IncidentsListPage.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Dedicated "Incidents" page (spec page 2, distinct from the Overview's top-5
 * preview and from the Incident Command Center's single-incident deep dive).
 * Shows every incident with severity, component, PO, a best-effort production
 * impact (client-side join against /production by affected_component — this
 * is a display join, not a risk calculation), and status.
 *
 * RECEIVES: GET /incidents, GET /production (src/api/incidents.js, production.js)
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
  const [severityFilter, setSeverityFilter] = useState("ALL");

  useEffect(() => {
    Promise.all([listIncidents("all"), listProductionOrders()])
      .then(([incidentsRes, productionsRes]) => {
        setIncidents(incidentsRes);
        setProductions(productionsRes);
      })
      .catch((err) => console.error("Incidents list load failed:", err))
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

  if (loading) return <p>Loading incidents…</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Incidents</h1>
          <div className="page-subtitle">{incidents.length} total · {filtered.length} shown</div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
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

      <div className="panel">
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
                      <Link to={`/incidents/${incident.incident_id}`} style={{ color: "var(--accent)", textDecoration: "none" }}>
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
