/**
 * src/components/common/KpiCard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Single KPI tile used on the Overview dashboard's top strip. `tone` picks the
 * top accent color so critical/at-risk numbers stand out without judges
 * having to read the label first.
 */
export default function KpiCard({ label, value, hint, tone }) {
  return (
    <div className={`kpi-card${tone ? ` tone-${tone}` : ""}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {hint && <div className="kpi-hint">{hint}</div>}
    </div>
  );
}