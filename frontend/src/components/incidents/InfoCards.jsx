/**
 * src/components/incidents/InfoCards.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `incident` prop, optional `plan` prop
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
    <div className="info-grid">
      <div className="panel info-card">
        <div className="kpi-label" style={{ fontSize: 11 }}>INVENTORY</div>
        <div className="info-card-body">Component: {incident.affected_component || "—"}</div>
        {inventory ? (
          <>
            <div className="info-card-body">Usable stock: <strong>{inventory.usable_stock}</strong> / {inventory.current_stock}</div>
            <div className="info-card-body">Daily usage: {inventory.daily_usage}</div>
            <div className="info-card-body" style={{ color: inventory.days_of_supply < 7 ? "var(--status-critical)" : "var(--text-primary)" }}>
              Days of supply: <strong>{inventory.days_of_supply ?? "—"}</strong>
            </div>
          </>
        ) : (
          <div className="info-card-empty">Loading inventory…</div>
        )}
      </div>

      <div className="panel info-card">
        <div className="kpi-label" style={{ fontSize: 11 }}>PRODUCTION</div>
        {productionOrders.length === 0 ? (
          <div className="info-card-empty">No production orders consume this component.</div>
        ) : (
          productionOrders.map((p) => (
            <div key={p.production_id} className="info-card-row">
              <strong>{p.production_id}</strong> — {p.product} · {p.priority} priority · {p.status}
              {p.deadline && <div className="info-card-sub">Deadline: {new Date(p.deadline).toLocaleDateString()}</div>}
            </div>
          ))
        )}
      </div>

      <div className="panel info-card">
        <div className="kpi-label" style={{ fontSize: 11 }}>SUPPLIER</div>
        {suppliers.length === 0 ? (
          <div className="info-card-empty">
            {plan ? "No supplier allocated in the recommended option." : "Supplier contact happens once the agent starts investigating."}
          </div>
        ) : (
          suppliers.map((s) => (
            <div key={s.supplier_id} className="info-card-row">
              <strong>{s.name}</strong> ({s.supplier_id})
              <div className="info-card-sub">Quality {s.quality_score} · Reliability {s.reliability_score}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}