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
import { useAuth } from "../../context/AuthContext.jsx";

const SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export default function IncidentsListPage() {
  const { activeWarehouse, currentUser } = useAuth();
  const [incidents, setIncidents] = useState([]);
  const [productions, setProductions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState("ALL");

  const load = () => {
    Promise.all([listIncidents("all"), listProductionOrders()])
      .then(([incidentsRes, productionsRes]) => {
        setIncidents(incidentsRes || []);
        setProductions(productionsRes || []);
      })
      .catch((err) => console.error("Incidents list load failed:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 3500);
    return () => clearInterval(interval);
  }, [activeWarehouse, currentUser]);

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
                    <td>
                      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        <StatusBadge status={incident.status} />
                        {incident.status === "RESOLVED" && incident.resolution_mode === "AUTONOMOUS" && (
                          <span
                            style={{
                              fontSize: 10,
                              fontWeight: 700,
                              padding: "2px 6px",
                              borderRadius: 4,
                              background: "rgba(16, 185, 129, 0.15)",
                              color: "#10B981",
                              border: "1px solid rgba(16, 185, 129, 0.35)",
                              display: "inline-block",
                              width: "fit-content",
                            }}
                            title={incident.autonomous_reasoning || "Resolved automatically within $50,000 threshold"}
                          >
                            🤖 Autonomous
                          </span>
                        )}
                        {incident.status === "RESOLVED" && incident.resolution_mode === "HUMAN_APPROVED" && (
                          <span
                            style={{
                              fontSize: 10,
                              fontWeight: 700,
                              padding: "2px 6px",
                              borderRadius: 4,
                              background: "rgba(245, 158, 11, 0.15)",
                              color: "#F59E0B",
                              border: "1px solid rgba(245, 158, 11, 0.35)",
                              display: "inline-block",
                              width: "fit-content",
                            }}
                            title={incident.autonomous_reasoning || "Approved by coordinator"}
                          >
                            👤 Human Sign-off
                          </span>
                        )}
                      </div>
                    </td>
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