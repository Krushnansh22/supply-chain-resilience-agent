/**
 * src/components/production/ProductionPage.jsx
 * Owner: Developer 4 (Frontend)
 * RECEIVES: GET /production (src/api/production.js)
 */
import { useEffect, useState } from "react";
import { listProductionOrders } from "../../api/production.js";

export default function ProductionPage() {
  const [rows, setRows] = useState([]);

  useEffect(() => { listProductionOrders().then(setRows).catch(console.error); }, []);

  return (
    <div className="panel">
      <h2>Production Orders</h2>
      <table style={{ width: "100%", fontSize: 13 }}>
        <thead>
          <tr>
            <th align="left">ID</th><th align="left">Product</th>
            <th align="left">Priority</th><th align="left">Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.production_id}>
              <td>{r.production_id}</td><td>{r.product}</td>
              <td>{r.priority}</td><td>{r.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
