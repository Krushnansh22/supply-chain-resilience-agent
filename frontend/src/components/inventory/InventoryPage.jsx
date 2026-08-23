/**
 * src/components/inventory/InventoryPage.jsx
 * Multi-Warehouse Inventory & Stock Telemetry
 */
import { useEffect, useState, useCallback } from "react";
import { listInventory } from "../../api/inventory.js";
import { useAuth } from "../../context/AuthContext.jsx";

export default function InventoryPage() {
  const { activeWarehouse, currentUser, isAdmin } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    listInventory()
      .then((data) => setRows(data || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(() => {
      if (document.visibilityState === "visible") {
        load();
      }
    }, 4000);
    return () => clearInterval(interval);
  }, [load, activeWarehouse, currentUser]);

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Inventory & Stock Telemetry</h1>
          <div className="page-subtitle">
            Showing components for: <strong>{activeWarehouse === "ALL" ? "🌐 All Global Warehouses" : `📍 ${activeWarehouse}`}</strong> ({rows.length} items)
          </div>
        </div>
        <div>
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              padding: "4px 12px",
              borderRadius: 6,
              background: isAdmin ? "rgba(35, 184, 201, 0.15)" : "rgba(245, 158, 11, 0.15)",
              color: isAdmin ? "#23B8C9" : "#F59E0B",
              border: isAdmin ? "1px solid rgba(35, 184, 201, 0.4)" : "1px solid rgba(245, 158, 11, 0.4)",
            }}
          >
            {isAdmin ? "ADMIN: GLOBAL ACCESS" : `MANAGER: SCOPED TO ${activeWarehouse}`}
          </span>
        </div>
      </div>

      <div className="panel elevated-panel">
        {loading ? (
          <p className="empty-state">Loading inventory…</p>
        ) : rows.length === 0 ? (
          <p className="empty-state">No inventory records found for {activeWarehouse}.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Component</th>
                <th>Warehouse Location</th>
                <th>Usable Stock</th>
                <th>Safety Threshold</th>
                <th>Daily Usage</th>
                <th>Days of Supply</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => {
                const isNegative = r.usable_stock != null && r.usable_stock < 0;
                const isMissing = r.usable_stock == null;
                const isLow = r.usable_stock != null && r.usable_stock <= (r.safety_stock || 100);

                return (
                  <tr
                    key={r.component_id}
                    style={{
                      background: isNegative ? "rgba(239, 68, 68, 0.08)" : isMissing ? "rgba(245, 158, 11, 0.08)" : "inherit",
                    }}
                  >
                    <td>
                      <strong>{r.component_id}</strong>
                      {r.name && <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{r.name}</div>}
                    </td>
                    <td>
                      <span className="badge" style={{ background: "rgba(255,255,255,0.06)", color: "var(--text-primary)" }}>
                        📍 {r.location || "Warehouse-A"}
                      </span>
                    </td>
                    <td>
                      {isNegative ? (
                        <span className="badge badge-critical" style={{ fontWeight: 700 }}>
                          📉 {r.usable_stock} units
                        </span>
                      ) : isMissing ? (
                        <span className="badge badge-warning">❓ Missing</span>
                      ) : (
                        <span>{r.usable_stock} / {r.current_stock ?? r.usable_stock}</span>
                      )}
                    </td>
                    <td>{r.safety_stock ?? 100} units</td>
                    <td>{r.daily_usage ?? "—"} / day</td>
                    <td>
                      <span className={isNegative || (r.days_of_supply != null && r.days_of_supply < 7) ? "badge badge-critical" : ""}>
                        {isNegative ? "DEFICIT" : r.days_of_supply ?? "—"}
                      </span>
                    </td>
                    <td>
                      {isNegative ? (
                        <span className="badge badge-critical">DATA ANOMALY</span>
                      ) : isMissing ? (
                        <span className="badge badge-warning">NO TELEMETRY</span>
                      ) : isLow ? (
                        <span className="badge badge-warning">LOW STOCK</span>
                      ) : (
                        <span className="badge badge-low">OPTIMAL</span>
                      )}
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