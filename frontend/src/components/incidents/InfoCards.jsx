/**
 * src/components/incidents/InfoCards.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 13: three info cards — INVENTORY / PRODUCTION / SUPPLIER.
 * RECEIVES: `incident` prop. TODO (Dev4): fetch the actual component/production/
 * supplier detail (src/api/inventory.js, production.js, suppliers.js) using
 * incident.affected_component — currently shows placeholders only.
 */
export default function InfoCards({ incident }) {
  return (
    <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
      <div className="panel" style={{ flex: 1 }}>
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>INVENTORY</div>
        <div>Component: {incident.affected_component}</div>
        <div style={{ color: "var(--text-muted)" }}>TODO: usable units / days coverage</div>
      </div>
      <div className="panel" style={{ flex: 1 }}>
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>PRODUCTION</div>
        <div style={{ color: "var(--text-muted)" }}>TODO: production order / priority / deadline</div>
      </div>
      <div className="panel" style={{ flex: 1 }}>
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>SUPPLIER</div>
        <div style={{ color: "var(--text-muted)" }}>TODO: supplier status / risk</div>
      </div>
    </div>
  );
}
