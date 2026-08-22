/**
 * src/components/suppliers/SuppliersPage.jsx
 * Owner: Developer 4 (Frontend)
 * RECEIVES: GET /suppliers (src/api/suppliers.js)
 */
import { useEffect, useState } from "react";
import { listSuppliers } from "../../api/suppliers.js";

export default function SuppliersPage() {
  const [rows, setRows] = useState([]);

  useEffect(() => { listSuppliers().then(setRows).catch(console.error); }, []);

  return (
    <div className="panel">
      <h2>Suppliers</h2>
      <table style={{ width: "100%", fontSize: 13 }}>
        <thead>
          <tr>
            <th align="left">ID</th><th align="left">Name</th>
            <th align="left">Quality</th><th align="left">Reliability</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.supplier_id}>
              <td>{r.supplier_id}</td><td>{r.name}</td>
              <td>{r.quality_score}</td><td>{r.reliability_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
