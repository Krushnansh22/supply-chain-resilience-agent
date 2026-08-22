/**
 * src/components/overview/KpiCards.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 12: Active incidents / Production coverage / Financial exposure /
 * Production continuity-risk.
 *
 * RECEIVES: `incidents` prop from OverviewDashboard
 * TODO (Dev4 + Dev3): production coverage & financial exposure need real aggregation —
 * either a dedicated backend endpoint (recommend: GET /incidents/summary) or client-side
 * computation once /production and /inventory data is joined. Placeholder shows counts only.
 */
export default function KpiCards({ incidents }) {
  const activeCount = incidents.filter((i) => i.status !== "RESOLVED").length;

  return (
    <div style={{ display: "flex", gap: 16 }}>
      <div className="panel" style={{ flex: 1 }}>
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>ACTIVE INCIDENTS</div>
        <div style={{ fontSize: 32 }}>{activeCount}</div>
      </div>
      <div className="panel" style={{ flex: 1 }}>
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>PRODUCTION COVERAGE</div>
        <div style={{ fontSize: 32 }}>— TODO</div>
      </div>
      <div className="panel" style={{ flex: 1 }}>
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>FINANCIAL EXPOSURE</div>
        <div style={{ fontSize: 32 }}>— TODO</div>
      </div>
      <div className="panel" style={{ flex: 1 }}>
        <div style={{ color: "var(--text-muted)", fontSize: 12 }}>PRODUCTION RISK</div>
        <div style={{ fontSize: 32 }}>— TODO</div>
      </div>
    </div>
  );
}
