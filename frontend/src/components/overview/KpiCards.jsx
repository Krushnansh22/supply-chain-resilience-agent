/**
 * src/components/overview/KpiCards.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Exact visual match to the 4 KPI cards in the reference screenshot:
 *  1. Current balance ($999,999 | Today profit +$123,123 +10.05%)
 *  2. Income ($223,324 | Today +$142,245 +23.23%)
 *  3. Expence ($123,434 | Today -$123,123 -10.05%)
 *  4. Nearest delivery (26.12.23 | Responsible for delivery + Driver avatars)
 */

export default function KpiCards({ incidents = [], productionOrders = [], suppliers = [] }) {
  const activeIncidents = incidents.filter((i) => i.status !== "RESOLVED");
  const criticalCount = activeIncidents.filter((i) => i.severity === "CRITICAL").length;
  const highCount = activeIncidents.filter((i) => i.severity === "HIGH").length;

  // Derive dynamic balance/resilience values
  const resilienceScore = Math.max(
    0,
    Math.min(100, Math.round(100 - criticalCount * 15 - highCount * 8 - (activeIncidents.length - criticalCount - highCount) * 3))
  );

  return (
    <div className="kpi-row-grid">
      {/* ── Card 1: Current balance ── */}
      <div className="kpi-stat-card">
        <div className="kpi-header">
          <div className="kpi-icon-circle blue">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
          </div>
          <span className="kpi-title-text">Current balance</span>
        </div>

        <div className="kpi-amount-val">$999,999</div>

        <div className="kpi-footer-row">
          <span className="kpi-sub-text">Today profit</span>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: "var(--green-accent)", fontWeight: 700 }}>+$123,123</span>
            <span className="kpi-trend-pill positive">+10.05%</span>
          </div>
        </div>
      </div>

      {/* ── Card 2: Income ── */}
      <div className="kpi-stat-card">
        <div className="kpi-header">
          <div className="kpi-icon-circle green">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/>
              <path d="M12 18V6"/>
            </svg>
          </div>
          <span className="kpi-title-text">Income</span>
        </div>

        <div className="kpi-amount-val">$223,324</div>

        <div className="kpi-footer-row">
          <span className="kpi-sub-text">Today</span>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: "var(--green-accent)", fontWeight: 700 }}>+$142,245</span>
            <span className="kpi-trend-pill positive">+23.23%</span>
          </div>
        </div>
      </div>

      {/* ── Card 3: Expence ── */}
      <div className="kpi-stat-card">
        <div className="kpi-header">
          <div className="kpi-icon-circle red">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20"/>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
          </div>
          <span className="kpi-title-text">Expence</span>
        </div>

        <div className="kpi-amount-val">$123,434</div>

        <div className="kpi-footer-row">
          <span className="kpi-sub-text">Today</span>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: "var(--red-accent)", fontWeight: 700 }}>-$123,123</span>
            <span className="kpi-trend-pill negative">-10.05%</span>
          </div>
        </div>
      </div>

      {/* ── Card 4: Nearest delivery ── */}
      <div className="kpi-stat-card">
        <div className="kpi-header">
          <div className="kpi-icon-circle yellow">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
          </div>
          <span className="kpi-title-text">Nearest delivery</span>
        </div>

        <div className="kpi-amount-val">26.12.23</div>

        <div className="kpi-footer-row">
          <span className="kpi-sub-text">Responsible for delivery</span>
          <div className="avatar-stack">
            <img
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&auto=format&fit=crop&q=80"
              alt="Driver 1"
              className="avatar-stack-img"
            />
            <img
              src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=80&auto=format&fit=crop&q=80"
              alt="Driver 2"
              className="avatar-stack-img"
            />
            <div
              className="avatar-stack-img"
              style={{
                background: "#F1F5F9",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 10,
                fontWeight: 700,
                color: "var(--text-secondary)"
              }}
            >
              +2
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
