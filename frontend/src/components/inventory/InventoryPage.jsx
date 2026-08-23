import { useEffect, useState } from "react";
import { listInventory } from "../../api/inventory.js";

export default function InventoryPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listInventory().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  const criticalCount = rows.filter(r => r.days_of_supply != null && r.days_of_supply < 7).length;
  const warningCount = rows.filter(r => r.days_of_supply != null && r.days_of_supply >= 7 && r.days_of_supply < 14).length;

  return (
    <div className="page-container">
      <div className="page-header" style={{ marginBottom: "20px" }}>
        <div>
          <h1>Component Inventory</h1>
          <div className="page-subtitle">Real-time stock levels, daily burn rates, and buffer safety margins</div>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <span className="badge badge-info">{rows.length} SKUs Tracked</span>
        </div>
      </div>

      {/* KPI stats */}
      <div className="kpi-row-grid" style={{ marginBottom: "24px" }}>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle blue">📦</div>
            <span className="kpi-title-text">Tracked Components</span>
          </div>
          <div className="kpi-amount-val">{rows.length}</div>
          <div className="kpi-footer-row"><span>Active BOM items</span></div>
        </div>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle red">⚠️</div>
            <span className="kpi-title-text">Critical Stockout Risk</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--red-accent)" }}>{criticalCount}</div>
          <div className="kpi-footer-row"><span>&lt; 7 days of supply</span></div>
        </div>
        <div className="kpi-stat-card">
          <div className="kpi-header">
            <div className="kpi-icon-circle yellow">⏱️</div>
            <span className="kpi-title-text">Low Buffer Stock</span>
          </div>
          <div className="kpi-amount-val" style={{ color: "var(--amber-accent)" }}>{warningCount}</div>
          <div className="kpi-footer-row"><span>7 to 14 days of supply</span></div>
        </div>
      </div>

      <div className="dashboard-card" style={{ padding: 0, overflow: "hidden" }}>
        <div className="card-header-row" style={{ padding: "16px 20px", borderBottom: "1px solid var(--border-subtle)" }}>
          <h3 className="card-header-title" style={{ margin: 0 }}>Inventory Balance & Burn Rate</h3>
        </div>

        {loading ? (
          <div style={{ padding: "40px", textAlign: "center" }}>
            <span className="loading-orb" />
            <p className="empty-state">Loading component stock...</p>
          </div>
        ) : (
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th>Component SKU</th>
                  <th>Usable / Total Stock</th>
                  <th>Daily Usage</th>
                  <th>Days of Supply</th>
                  <th>Stock Health</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => {
                  const isCritical = r.days_of_supply != null && r.days_of_supply < 7;
                  const isWarning = r.days_of_supply != null && r.days_of_supply >= 7 && r.days_of_supply < 14;
                  return (
                    <tr key={r.component_id}>
                      <td>
                        <span className="code-chip" style={{ fontWeight: 700 }}>{r.component_id}</span>
                      </td>
                      <td style={{ fontWeight: 600 }}>
                        {r.usable_stock?.toLocaleString()} <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>/ {r.current_stock?.toLocaleString()}</span>
                      </td>
                      <td>{r.daily_usage?.toLocaleString()} units/day</td>
                      <td>
                        <span style={{ fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                          {r.days_of_supply != null ? `${r.days_of_supply} days` : "—"}
                        </span>
                      </td>
                      <td>
                        {isCritical ? (
                          <span className="badge badge-critical">CRITICAL DEFICIT</span>
                        ) : isWarning ? (
                          <span className="badge badge-warning">LOW BUFFER</span>
                        ) : (
                          <span className="badge badge-success">HEALTHY</span>
                        )}
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