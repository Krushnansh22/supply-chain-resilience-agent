import { useEffect, useState } from "react";
import { listProductionOrders } from "../../api/production.js";

export default function ProductionPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState("production_id");
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    listProductionOrders().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  const criticalCount = rows.filter(r => r.priority === "CRITICAL" || r.priority === "HIGH").length;
  const onTrackCount = rows.filter(r => r.status === "ON_TRACK" || r.status === "COMPLETED").length;

  const handleSort = (field) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const filtered = rows.filter((r) =>
    r.production_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.product?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.component_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.status?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => {
    const valA = a[sortField] ?? "";
    const valB = b[sortField] ?? "";
    return sortAsc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
  });

  return (
    <div className="page-container">
      <div className="page-header" style={{ marginBottom: "20px" }}>
        <div>
          <h1>Production Schedule & Work Orders</h1>
          <div className="page-subtitle">Manufacturing line commitments, component dependencies, and build status</div>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <span className="badge badge-info">{rows.length} Work Orders Active</span>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="kpi-row-grid" style={{ marginBottom: "24px" }}>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle blue">🏭</div>
            <span className="kpi-title-text">Active Runs</span>
          </div>
          <div className="kpi-amount-val">{rows.length}</div>
          <div className="kpi-footer-row"><span>Scheduled assembly lines</span></div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle green">✅</div>
            <span className="kpi-title-text">On-Track</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--emerald-accent)" }}>{onTrackCount}</div>
          <div className="kpi-footer-row"><span>Meeting target SLA</span></div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle red">🔥</div>
            <span className="kpi-title-text">High Priority Lines</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--red-accent)" }}>{criticalCount}</div>
          <div className="kpi-footer-row"><span>Tier-1 customer commitments</span></div>
        </div>
      </div>

      <div className="dashboard-card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="card-header-row" style={{ padding: "16px 20px", borderBottom: "1px solid var(--border-subtle)", flexWrap: "wrap", gap: 12 }}>
          <h3 className="card-header-title" style={{ margin: 0 }}>Work Order Registry</h3>
          <div style={{ marginLeft: "auto" }}>
            <input
              type="text"
              placeholder="Search product or line..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                border: "1px solid var(--border-subtle)",
                fontSize: "12px",
                width: "200px",
              }}
            />
          </div>
        </div>

        {loading ? (
          <div style={{ padding: "40px", textAlign: "center" }}>
            <span className="loading-orb" />
            <p className="empty-state">Loading production schedule...</p>
          </div>
        ) : (
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort("production_id")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Order ID {sortField === "production_id" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("product")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Product Assembly {sortField === "product" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("component_id")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Required Component {sortField === "component_id" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("priority")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Priority {sortField === "priority" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th>Target Deadline</th>
                  <th onClick={() => handleSort("status")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Line Status {sortField === "status" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((r) => (
                  <tr key={r.production_id}>
                    <td>
                      <span className="code-chip" style={{ fontWeight: 700 }}>{r.production_id}</span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{r.product}</td>
                    <td>
                      <span className="code-chip">{r.component_id}</span>
                    </td>
                    <td>
                      <span className={`badge ${
                        r.priority === "CRITICAL" ? "badge-critical" :
                        r.priority === "HIGH" ? "badge-high" :
                        "badge-neutral"
                      }`}>
                        {r.priority}
                      </span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "12px" }}>
                      {r.deadline ? new Date(r.deadline).toLocaleDateString() : "—"}
                    </td>
                    <td>
                      <span className={`badge ${
                        r.status === "ON_TRACK" ? "badge-success" :
                        r.status === "BLOCKED" || r.status === "WAITING_PARTS" ? "badge-critical" :
                        "badge-warning"
                      }`}>
                        {r.status?.replaceAll("_", " ")}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}