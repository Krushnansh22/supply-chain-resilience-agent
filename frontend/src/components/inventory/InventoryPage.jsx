import { useEffect, useState } from "react";
import { listInventory } from "../../api/inventory.js";

export default function InventoryPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState("component_id");
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    listInventory().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  const criticalCount = rows.filter(r => r.days_of_supply != null && r.days_of_supply < 7).length;
  const warningCount = rows.filter(r => r.days_of_supply != null && r.days_of_supply >= 7 && r.days_of_supply < 14).length;

  const handleSort = (field) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const filtered = rows.filter((r) =>
    r.component_id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const sorted = [...filtered].sort((a, b) => {
    const valA = a[sortField] ?? "";
    const valB = b[sortField] ?? "";
    if (typeof valA === "number" && typeof valB === "number") {
      return sortAsc ? valA - valB : valB - valA;
    }
    return sortAsc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
  });

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
        <div className="card-header-row" style={{ padding: "16px 20px", borderBottom: "1px solid var(--border-subtle)", flexWrap: "wrap", gap: 12 }}>
          <h3 className="card-header-title" style={{ margin: 0 }}>Inventory Balance & Burn Rate</h3>
          <div style={{ marginLeft: "auto" }}>
            <input
              type="text"
              placeholder="Filter by SKU..."
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
            <p className="empty-state">Loading component stock...</p>
          </div>
        ) : (
          <div className="deliveries-table-wrap">
            <table className="custom-data-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort("component_id")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Component SKU {sortField === "component_id" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("usable_stock")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Usable / Total Stock {sortField === "usable_stock" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("daily_usage")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Daily Usage {sortField === "daily_usage" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th onClick={() => handleSort("days_of_supply")} style={{ cursor: "pointer", userSelect: "none" }}>
                    Days of Supply {sortField === "days_of_supply" ? (sortAsc ? "▲" : "▼") : ""}
                  </th>
                  <th>Stock Health</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((r) => {
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