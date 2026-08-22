/**
 * src/components/inventory/InventoryPage.jsx
 * Owner: Developer 4 (Frontend)
 * RECEIVES: GET /inventory (src/api/inventory.js)
 */
import { useEffect, useState } from "react";
import { listInventory } from "../../api/inventory.js";

export default function InventoryPage() {
  const [rows, setRows] = useState([]);

  useEffect(() => { listInventory().then(setRows).catch(console.error); }, []);

  return (
    <div className="panel">
      <h2>Inventory</h2>
      <table style={{ width: "100%", fontSize: 13 }}>
        <thead>
          <tr>
            <th align="left">Component</th><th align="left">Usable Stock</th>
            <th align="left">Daily Usage</th><th align="left">Days of Supply</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.component_id}>
              <td>{r.component_id}</td><td>{r.usable_stock}</td>
              <td>{r.daily_usage}</td><td>{r.days_of_supply}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
