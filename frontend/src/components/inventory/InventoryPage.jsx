/**
 * src/components/inventory/InventoryPage.jsx
 * Owner: Developer 4 (Frontend)
 * RECEIVES: GET /inventory (src/api/inventory.js)
 */
import { useEffect, useState } from "react";
import { listInventory } from "../../api/inventory.js";

export default function InventoryPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listInventory().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Inventory</h1>
          <div className="page-subtitle">{rows.length} components tracked</div>
        </div>
      </div>
      <div className="panel">
        {loading ? (
          <p className="empty-state">Loading inventory…</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Component</th><th>Usable Stock</th><th>Daily Usage</th><th>Days of Supply</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.component_id}>
                  <td>{r.component_id}</td>
                  <td>{r.usable_stock} / {r.current_stock}</td>
                  <td>{r.daily_usage}</td>
                  <td>
                    <span className={r.days_of_supply != null && r.days_of_supply < 7 ? "badge badge-critical" : ""}>
                      {r.days_of_supply ?? "—"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
