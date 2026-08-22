/**
 * src/components/incidents/InfoCards.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 13: three info cards — INVENTORY / PRODUCTION / SUPPLIER.
 * RECEIVES: `incident` prop, optional `plan` prop (once a RecoveryPlan exists,
 *   used to surface which suppliers the agent is working with).
 *   - GET /inventory/{component_id}  (src/api/inventory.js)
 *   - GET /production                (src/api/production.js, filtered client-side
 *     by component_id — display join only, no risk calculation)
 *   - GET /suppliers/{supplier_id}   (src/api/suppliers.js, one per allocation
 *     in the plan's recommended option)
 */
import { useEffect, useState } from "react";
import { getComponent } from "../../api/inventory.js";
import { listProductionOrders } from "../../api/production.js";
import { getSupplier } from "../../api/suppliers.js";

export default function InfoCards({ incident, plan }) {
  const [inventory, setInventory] = useState(null);
  const [productionOrders, setProductionOrders] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {
    if (incident.affected_component) {
      getComponent(incident.affected_component).then(setInventory).catch(() => setInventory(null));
      listProductionOrders()
        .then((rows) => setProductionOrders(rows.filter((r) => r.component_id === incident.affected_component)))
        .catch(() => setProductionOrders([]));
    }
  }, [incident.affected_component]);

  useEffect(() => {
    const recommended = plan?.options.find((o) => o.option_id === plan.recommended_option_id);
    const supplierIds = recommended?.allocations.map((a) => a.supplier_id) || [];
    if (supplierIds.length === 0) { setSuppliers([]); return; }
    Promise.all(supplierIds.map((id) => getSupplier(id).catch(() => null)))
      .then((rows) => setSuppliers(rows.filter(Boolean)));
  }, [plan]);

  return (
    <div style={{ display: "flex", gap: 16, marginTop: 16, flexWrap: "wrap" }}>
      <div className="panel" style={{ flex: 1, minWidth: 220 }}>
        <div className="kpi-label" style={{ fontSize: 11 }}>INVENTORY</div>
        <div>Component: {incident.affected_component || "—"}</div>
        {inventory ? (
          <>
            <div>Usable stock: <strong>{inventory.usable_stock}</strong> / {inventory.current_stock}</div>
            <div>Daily usage: {inventory.daily_usage}</div>
            <div style={{ color: inventory.days_of_supply < 7 ? "var(--status-critical)" : "var(--text-primary)" }}>
              Days of supply: <strong>{inventory.days_of_supply ?? "—"}</strong>
            </div>
          </>
        ) : (
          <div style={{ color: "var(--text-muted)" }}>Loading inventory…</div>
        )}
      </div>

      <div className="panel" style={{ flex: 1, minWidth: 220 }}>
        <div className="kpi-label" style={{ fontSize: 11 }}>PRODUCTION</div>
        {productionOrders.length === 0 ? (
          <div style={{ color: "var(--text-muted)" }}>No production orders consume this component.</div>
        ) : (
          productionOrders.map((p) => (
            <div key={p.production_id} style={{ fontSize: 13, padding: "4px 0", borderTop: "1px solid var(--border-subtle)" }}>
              <strong>{p.production_id}</strong> — {p.product} · {p.priority} priority · {p.status}
              {p.deadline && <div style={{ color: "var(--text-muted)" }}>Deadline: {new Date(p.deadline).toLocaleDateString()}</div>}
            </div>
          ))
        )}
      </div>

      <div className="panel" style={{ flex: 1, minWidth: 220 }}>
        <div className="kpi-label" style={{ fontSize: 11 }}>SUPPLIER</div>
        {suppliers.length === 0 ? (
          <div style={{ color: "var(--text-muted)" }}>
            {plan ? "No supplier allocated in the recommended option." : "Supplier contact happens once the agent starts investigating."}
          </div>
        ) : (
          suppliers.map((s) => (
            <div key={s.supplier_id} style={{ fontSize: 13, padding: "4px 0", borderTop: "1px solid var(--border-subtle)" }}>
              <strong>{s.name}</strong> ({s.supplier_id})
              <div style={{ color: "var(--text-secondary)" }}>Quality {s.quality_score} · Reliability {s.reliability_score}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
