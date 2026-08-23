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
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState("severity");
  const [sortAsc, setSortAsc] = useState(true);

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

  // Statistics counters
  const stats = useMemo(() => {
    const total = incidents.length;
    const critical = incidents.filter(i => i.severity === "CRITICAL").length;
    const high = incidents.filter(i => i.severity === "HIGH").length;
    const waiting = incidents.filter(i => i.status === "WAITING_APPROVAL").length;
    const active = incidents.filter(i => i.status !== "RESOLVED" && i.status !== "CANCELLED").length;
    return { total, critical, high, waiting, active };
  }, [incidents]);

  const filtered = useMemo(() => {
    return incidents.filter((incident) => {
      if (severityFilter !== "ALL" && incident.severity !== severityFilter) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesId = incident.incident_id?.toLowerCase().includes(q);
        const matchesType = incident.type?.toLowerCase().includes(q);
        const matchesComponent = incident.affected_component?.toLowerCase().includes(q);
        const matchesPO = incident.affected_po?.toLowerCase().includes(q);
        const matchesStatus = incident.status?.toLowerCase().includes(q);
        return matchesId || matchesType || matchesComponent || matchesPO || matchesStatus;
      }
      return true;
    });
  }, [incidents, severityFilter, searchQuery]);

  const handleSort = (field) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const sortedFiltered = useMemo(() => {
    return [...filtered].sort((a, b) => {
      let valA = a[sortField] || "";
      let valB = b[sortField] || "";
      if (sortField === "severity") {
        valA = SEVERITY_ORDER.indexOf(valA);
        valB = SEVERITY_ORDER.indexOf(valB);
        return sortAsc ? valA - valB : valB - valA;
      }
      return sortAsc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
    });
  }, [filtered, sortField, sortAsc]);

  if (loading) {
    return (
      <div className="loading-shell">
        <span className="loading-orb" />
        <span>Loading incident control tower…</span>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header Banner */}
      <div className="page-header" style={{ marginBottom: "20px" }}>
        <div>
          <h1>Disruption Incidents</h1>
          <div className="page-subtitle">
            Autonomous triage, supplier delivery anomalies, and mitigation tracking
          </div>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <span className="badge badge-info">LIVE TELEMETRY</span>
        </div>
      </div>

      {/* KPI Stats Ribbon */}
      <div className="kpi-row-grid" style={{ marginBottom: "24px" }}>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle blue">🚨</div>
            <span className="kpi-title-text">Active Incidents</span>
          </div>
          <div className="kpi-amount-val">{stats.active}</div>
          <div className="kpi-footer-row">
            <span>{stats.total} total logged</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle red">🔥</div>
            <span className="kpi-title-text">Critical Severity</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--red-accent)" }}>{stats.critical}</div>
          <div className="kpi-footer-row">
            <span>Immediate risk</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle yellow">⚠️</div>
            <span className="kpi-title-text">High Severity</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--amber-accent)" }}>{stats.high}</div>
          <div className="kpi-footer-row">
            <span>Line stoppage hazard</span>
          </div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle purple">⏳</div>
            <span className="kpi-title-text">Awaiting Approval</span>
          </div>
          <div className="kpi-amount-val">{stats.waiting}</div>
          <div className="kpi-footer-row">
            <span>Human coordinator sign-off</span>
          </div>
        </div>
      </div>

      {/* Control Bar: Search & Severity Filters */}
      <div className="dashboard-card" style={{ marginBottom: "20px", padding: "16px 20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "16px" }}>
          {/* Severity Pills */}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--text-muted)", marginRight: "4px", textTransform: "uppercase" }}>
              Filter:
            </span>
            {["ALL", ...SEVERITY_ORDER].map((s) => {
              const count = s === "ALL" ? incidents.length : incidents.filter(i => i.severity === s).length;
              return (
                <button
                  key={s}
                  className={`pill-filter${severityFilter === s ? " active" : ""}`}
                  onClick={() => setSeverityFilter(s)}
                >
                  <span>{s}</span>
                  <span style={{
                    fontSize: "10px",
                    background: severityFilter === s ? "rgba(255,255,255,0.3)" : "var(--bg-canvas)",
                    padding: "1px 6px",
                    borderRadius: "10px"
                  }}>
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Search Box */}
          <div style={{ minWidth: "260px", flexGrow: 1, maxWidth: "360px" }}>
            <input
              type="text"
              placeholder="Search by ID, component, PO, status..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 14px",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border-medium)",
                fontSize: "13px",
                background: "#FFFFFF",
                outline: "none"
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Incidents Table */}
      <div className="dashboard-card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="card-header-row" style={{ padding: "16px 20px", borderBottom: "1px solid var(--border-subtle)" }}>
          <h3 className="card-header-title" style={{ margin: 0 }}>
            Incident Ledger ({filtered.length} visible)
          </h3>
        </div>

        {filtered.length === 0 ? (
          <div style={{ padding: "40px 20px", textAlign: "center" }}>
            <p className="empty-state" style={{ marginBottom: "12px" }}>No incidents match the active filters.</p>
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => { setSeverityFilter("ALL"); setSearchQuery(""); }}
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort("severity")} style={{ width: "110px", cursor: "pointer", userSelect: "none" }}>
                    Severity {sortField === "severity" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("incident_id")} style={{ minWidth: "160px", cursor: "pointer", userSelect: "none" }}>
                    Incident Reference {sortField === "incident_id" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("affected_component")} style={{ width: "130px", cursor: "pointer", userSelect: "none" }}>
                    Component {sortField === "affected_component" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("affected_po")} style={{ width: "130px", cursor: "pointer", userSelect: "none" }}>
                    Purchase Order {sortField === "affected_po" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th style={{ minWidth: "240px" }}>Production Line Impact</th>
                  <th onClick={() => handleSort("status")} style={{ width: "140px", cursor: "pointer", userSelect: "none" }}>
                    Status {sortField === "status" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th style={{ width: "100px", textAlign: "right" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {sortedFiltered.map((incident) => {
                  const affected = productionByComponent[incident.affected_component] || [];
                  return (
                    <tr key={incident.incident_id}>
                      <td>
                        <SeverityBadge severity={incident.severity} />
                      </td>
                      <td>
                        <Link
                          to={`/incidents/${incident.incident_id}`}
                          style={{
                            color: "var(--primary)",
                            textDecoration: "none",
                            fontWeight: 700,
                            fontFamily: "var(--font-mono)",
                            fontSize: "13px"
                          }}
                        >
                          {incident.incident_id}
                        </Link>
                        <div style={{ color: "var(--text-secondary)", fontSize: "11px", marginTop: "2px", textTransform: "capitalize" }}>
                          {incident.type?.replaceAll("_", " ").toLowerCase()}
                        </div>
                      </td>
                      <td>
                        {incident.affected_component ? (
                          <span className="code-chip">{incident.affected_component}</span>
                        ) : (
                          <span style={{ color: "var(--text-muted)" }}>—</span>
                        )}
                      </td>
                      <td>
                        {incident.affected_po ? (
                          <span className="code-chip">{incident.affected_po}</span>
                        ) : (
                          <span style={{ color: "var(--text-muted)" }}>—</span>
                        )}
                      </td>
                      <td>
                        {affected.length === 0 ? (
                          <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>No active line stalled</span>
                        ) : (
                          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                            {affected.map((p) => (
                              <div key={p.production_id} className="production-impact-tag">
                                <span style={{ fontWeight: 600, fontFamily: "var(--font-mono)", fontSize: "11px" }}>
                                  {p.production_id}
                                </span>
                                <span style={{ color: "var(--text-secondary)", fontSize: "12px" }}>· {p.product}</span>
                                <span className={`badge ${p.priority === "CRITICAL" ? "badge-critical" : "badge-neutral"}`} style={{ padding: "1px 6px", fontSize: "9px" }}>
                                  {p.priority}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </td>
                      <td>
                        <StatusBadge status={incident.status} />
                      </td>
                      <td style={{ textAlign: "right" }}>
                        <Link
                          to={`/incidents/${incident.incident_id}`}
                          className="btn btn-ghost btn-sm"
                          style={{ fontSize: "12px", padding: "4px 10px", whiteSpace: "nowrap" }}
                        >
                          Inspect →
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}