import { useEffect, useState } from "react";
import { listSuppliers } from "../../api/suppliers.js";

export default function SuppliersPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listSuppliers().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  const avgQuality = rows.length > 0 ? (rows.reduce((acc, r) => acc + (r.quality_score || 0), 0) / rows.length).toFixed(1) : 0;
  const avgReliability = rows.length > 0 ? (rows.reduce((acc, r) => acc + (r.reliability_score || 0), 0) / rows.length).toFixed(1) : 0;

  return (
    <div className="page-container">
      <div className="page-header" style={{ marginBottom: "20px" }}>
        <div>
          <h1>Supplier Network & Trust Ratings</h1>
          <div className="page-subtitle">Historical quality metrics, on-time delivery records, and batch capacities</div>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <span className="badge badge-info">{rows.length} Verified Vendors</span>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="kpi-row-grid" style={{ marginBottom: "24px" }}>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle blue">🤝</div>
            <span className="kpi-title-text">Active Suppliers</span>
          </div>
          <div className="kpi-amount-val">{rows.length}</div>
          <div className="kpi-footer-row"><span>Contracted vendor partners</span></div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle green">⭐</div>
            <span className="kpi-title-text">Network Quality Avg</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--emerald-accent)" }}>{avgQuality}%</div>
          <div className="kpi-footer-row"><span>SCDA quality benchmark</span></div>
        </div>

        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle yellow">📊</div>
            <span className="kpi-title-text">Network Reliability Avg</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--amber-accent)" }}>{avgReliability}%</div>
          <div className="kpi-footer-row"><span>Delivery commitment index</span></div>
        </div>
      </div>

      <div className="dashboard-card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="card-header-row" style={{ padding: "16px 20px", borderBottom: "1px solid var(--border-subtle)" }}>
          <h3 className="card-header-title" style={{ margin: 0 }}>Supplier Performance Scorecards</h3>
        </div>

        {loading ? (
          <div style={{ padding: "40px", textAlign: "center" }}>
            <span className="loading-orb" />
            <p className="empty-state">Loading vendor records...</p>
          </div>
        ) : (
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th>Vendor ID</th>
                  <th>Company Name</th>
                  <th>Quality Score</th>
                  <th>Reliability Score</th>
                  <th>Minimum Order Qty</th>
                  <th>Certifications</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.supplier_id}>
                    <td>
                      <span className="code-chip" style={{ fontWeight: 700 }}>{r.supplier_id}</span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{r.name}</td>
                    <td>
                      <span style={{ fontWeight: 700, color: (r.quality_score || 0) >= 90 ? "var(--emerald-accent)" : "var(--amber-accent)" }}>
                        {r.quality_score != null ? `${r.quality_score}%` : "—"}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontWeight: 700, color: (r.reliability_score || 0) >= 85 ? "var(--emerald-accent)" : "var(--amber-accent)" }}>
                        {r.reliability_score != null ? `${r.reliability_score}%` : "—"}
                      </span>
                    </td>
                    <td>{r.min_order_qty != null ? `${r.min_order_qty.toLocaleString()} units` : "—"}</td>
                    <td>
                      <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                        {r.certifications || "ISO9001 Standard"}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-success">ACTIVE</span>
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