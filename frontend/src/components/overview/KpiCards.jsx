/**
 * src/components/overview/KpiCards.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Four rich Control Tower KPI cards: Network Resilience Score, Supplier Risk
 * Heatmap, Production Risk Index, Decision Overview — all derived live from
 * the same data the rest of the dashboard uses.
 *
 * RECEIVES: `incidents` (GET /incidents), `productionOrders` (GET /production),
 *           `suppliers` (GET /suppliers)
 */
export default function KpiCards({ incidents, productionOrders, suppliers }) {
  const activeIncidents = incidents.filter((i) => i.status !== "RESOLVED");
  const criticalCount = activeIncidents.filter((i) => i.severity === "CRITICAL").length;
  const highCount = activeIncidents.filter((i) => i.severity === "HIGH").length;

  // Network resilience score: starts at 100, docked for open incidents by severity.
  const resilienceScore = Math.max(
    0,
    Math.min(100, Math.round(100 - criticalCount * 15 - highCount * 8 - (activeIncidents.length - criticalCount - highCount) * 3))
  );

  // Supplier risk heatmap: bucket by average of quality_score / reliability_score (0-100 scale).
  const supplierBuckets = suppliers.reduce(
    (acc, s) => {
      const avg = ((s.quality_score ?? 0) + (s.reliability_score ?? 0)) / 2;
      if (avg < 65) acc.red += 1;
      else if (avg < 85) acc.yellow += 1;
      else acc.green += 1;
      return acc;
    },
    { red: 0, yellow: 0, green: 0 }
  );
  const heatCells = [
    ...Array(Math.min(supplierBuckets.red, 6)).fill("red"),
    ...Array(Math.min(supplierBuckets.yellow, 6)).fill("yellow"),
    ...Array(Math.min(supplierBuckets.green, 4)).fill("green"),
  ].slice(0, 12);

  // Production risk index: share of orders not on track.
  const atRiskOrders = productionOrders.filter((p) => p.status !== "ON_TRACK").length;
  const riskPct = productionOrders.length ? Math.round((atRiskOrders / productionOrders.length) * 100) : 0;
  const riskLabel = riskPct >= 40 ? "High Risk" : riskPct >= 15 ? "Medium Risk" : "Low Risk";

  // Decision overview: resolved vs unresolved incidents.
  const resolvedCount = incidents.filter((i) => i.status === "RESOLVED").length;
  const unresolvedCount = incidents.length - resolvedCount;
  const resolvedPct = incidents.length ? Math.round((resolvedCount / incidents.length) * 100) : 0;

  return (
    <div className="kpi-grid">
      <div className="kpi-card">
        <div className="kpi-body">
          <div className="kpi-label">Network Resilience Score</div>
          <div className="kpi-value">{resilienceScore}%</div>
          <div className="kpi-hint">{activeIncidents.length} open incident{activeIncidents.length === 1 ? "" : "s"}</div>
        </div>
        <div className="kpi-gauge" style={{ "--pct": resilienceScore }} />
      </div>

      <div className="kpi-card">
        <div className="kpi-body">
          <div className="kpi-label">Supplier Risk Heatmap</div>
          <div className="kpi-value">{supplierBuckets.red}</div>
          <div className="kpi-hint">
            {supplierBuckets.red} Red, {supplierBuckets.yellow} Yellow, {supplierBuckets.green} Green
          </div>
        </div>
        <div className="kpi-heat-grid">
          {heatCells.map((c, i) => (
            <div key={i} className={`heat-dot ${c}`} />
          ))}
        </div>
      </div>

      <div className="kpi-card" style={{ flexDirection: "column", alignItems: "stretch" }}>
        <div className="kpi-body">
          <div className="kpi-label">Production Risk Index</div>
          <div className="kpi-value tone-warning" style={{ color: "var(--warning)" }}>{riskPct}%</div>
          <div className="kpi-hint">{riskLabel}</div>
        </div>
        <div className="kpi-progress-track">
          <div className="kpi-progress-fill" style={{ width: `${riskPct}%` }} />
        </div>
        <div className="kpi-hint">of {productionOrders.length} total orders</div>
      </div>

      <div className="kpi-card">
        <div className="kpi-body">
          <div className="kpi-label">Decision Overview</div>
          <div className="kpi-value">{unresolvedCount} Unresolved</div>
          <div className="kpi-hint">{resolvedCount} Resolved</div>
        </div>
        <div className="kpi-donut" style={{ "--resolved": resolvedPct }} />
      </div>
    </div>
  );
}
