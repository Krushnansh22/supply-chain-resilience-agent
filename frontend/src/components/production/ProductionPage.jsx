/**
 * src/components/production/ProductionPage.jsx
 * Owner: Developer 4 (Frontend)
 */
import { useEffect, useState } from "react";
import { listProductionOrders } from "../../api/production.js";

export default function ProductionPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listProductionOrders().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Production Orders</h1>
          <div className="page-subtitle">{rows.length} orders</div>
        </div>
      </div>
      <div className="panel elevated-panel">
        {loading ? (
          <p className="empty-state">Loading production orders…</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th><th>Product</th><th>Component</th><th>Priority</th><th>Deadline</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.production_id}>
                  <td>{r.production_id}</td>
                  <td>{r.product}</td>
                  <td>{r.component_id}</td>
                  <td>{r.priority}</td>
                  <td>{r.deadline ? new Date(r.deadline).toLocaleDateString() : "—"}</td>
                  <td>
                    <span className={`badge ${r.status === "ON_TRACK" ? "badge-low" : "badge-high"}`}>{r.status}</span>
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