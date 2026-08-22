/**
 * src/components/suppliers/SuppliersPage.jsx
 * Owner: Developer 4 (Frontend)
 */
import { useEffect, useState } from "react";
import { listSuppliers } from "../../api/suppliers.js";

export default function SuppliersPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listSuppliers().then(setRows).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Suppliers</h1>
          <div className="page-subtitle">{rows.length} suppliers</div>
        </div>
      </div>
      <div className="panel elevated-panel">
        {loading ? (
          <p className="empty-state">Loading suppliers…</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th><th>Name</th><th>Quality</th><th>Reliability</th><th>MOQ</th><th>Certifications</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.supplier_id}>
                  <td>{r.supplier_id}</td>
                  <td>{r.name}</td>
                  <td>{r.quality_score}</td>
                  <td>{r.reliability_score}</td>
                  <td>{r.min_order_qty ?? "—"}</td>
                  <td style={{ color: "var(--text-secondary)" }}>{r.certifications || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}