import { useEffect, useState } from "react";
import { listProductionOrders } from "../../api/production.js";

export default function ProductionPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProductionOrders().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  const criticalCount = rows.filter(r => r.priority === "CRITICAL" || r.priority === "HIGH").length;
  const onTrackCount = rows.filter(r => r.status === "ON_TRACK" || r.status === "COMPLETED").length;

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
        <div className="card-header-row" style={{ padding: "16px 20px", borderBottom: "1px solid var(--border-subtle)" }}>
          <h3 className="card-header-title" style={{ margin: 0 }}>Work Order Registry</h3>
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
                  <th>Order ID</th>
                  <th>Product Assembly</th>
                  <th>Required Component</th>
                  <th>Priority</th>
                  <th>Target Deadline</th>
                  <th>Line Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
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