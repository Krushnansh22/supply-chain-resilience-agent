/**
 * src/components/overview/KpiCards.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 12 / spec Dashboard page: Active incidents / Critical
 * incidents / Production-at-risk count / Pending approvals. Everything here
 * is a plain count over data the backend already returns — no scoring or
 * risk calculation happens in React.
 *
 * RECEIVES: `incidents` (GET /incidents), `productionOrders` (GET /production)
 */
import KpiCard from "../common/KpiCard.jsx";

export default function KpiCards({ incidents, productionOrders }) {
  const activeStatuses = ["INVESTIGATING", "SUPPLIER_CONTACT", "EVALUATING", "PLAN_READY", "WAITING_APPROVAL", "EXECUTING", "REPLANNING"];
  const activeIncidents = incidents.filter((incident) => activeStatuses.includes(incident.status));
  const activeCount = activeIncidents.length;
  const criticalCount = activeIncidents.filter((i) => i.severity === "CRITICAL").length;
  const pendingApprovalsCount = incidents.filter((i) => i.status === "WAITING_APPROVAL").length;
  const productionAtRiskCount = productionOrders.filter((p) => p.status !== "ON_TRACK").length;

  return (
    <div className="kpi-grid">
      <KpiCard label="Active Incidents" value={activeCount} tone={activeCount > 0 ? "high" : undefined} />
      <KpiCard label="Critical Incidents" value={criticalCount} tone={criticalCount > 0 ? "critical" : undefined} />
      <KpiCard label="Production at Risk" value={productionAtRiskCount} hint={`of ${productionOrders.length} orders`} tone={productionAtRiskCount > 0 ? "high" : undefined} />
      <KpiCard label="Pending Approvals" value={pendingApprovalsCount} tone={pendingApprovalsCount > 0 ? "info" : undefined} />
    </div>
  );
}
