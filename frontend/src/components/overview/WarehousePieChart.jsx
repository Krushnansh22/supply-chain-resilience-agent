/**
 * src/components/overview/WarehousePieChart.jsx
 * Exact visual match to the Pie Chart card with Western, Central, and Reserve callout pills.
 */

export default function WarehousePieChart() {
  return (
    <div className="dashboard-card">
      {/* Header */}
      <div className="card-header-row">
        <span className="card-header-title">Warehouse workload</span>
        <div className="card-header-actions">
          {/* Funnel Filter Icon */}
          <button className="action-icon-btn" title="Filter">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
            </svg>
          </button>
          {/* More options 3 dots */}
          <button className="action-icon-btn" title="Options">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="5" cy="12" r="2"/>
              <circle cx="12" cy="12" r="2"/>
              <circle cx="19" cy="12" r="2"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Chart Graphic with Callout Labels */}
      <div className="pie-chart-container">
        {/* Western Pill (Cyan) */}
        <div className="chart-callout-pill cyan">
          Western
        </div>

        {/* Central Pill (Blue) */}
        <div className="chart-callout-pill blue">
          Central
        </div>

        {/* Reserve Pill (Yellow) */}
        <div className="chart-callout-pill yellow">
          Reserve
        </div>

        {/* SVG Pie Chart */}
        <svg viewBox="0 0 320 240" width="100%" height="100%" style={{ overflow: "visible" }}>
          {/* Connecting Line to Western */}
          <polyline
            points="65,40 115,40 140,85"
            fill="none"
            stroke="#00B4D8"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
          {/* Connecting Line to Central */}
          <polyline
            points="245,95 210,95 185,120"
            fill="none"
            stroke="#2563EB"
            strokeWidth="1.8"
            strokeLinecap="round"
          />
          {/* Connecting Line to Reserve */}
          <polyline
            points="70,185 110,185 130,160"
            fill="none"
            stroke="#F59E0B"
            strokeWidth="1.8"
            strokeLinecap="round"
          />

          {/* Pie Chart Group (Center: 160, 125, Radius: 75) */}
          <g transform="translate(160, 125)">
            {/* Slice 1: Blue (Central) - ~55% of the pie */}
            {/* Path from -30 deg to 170 deg */}
            <path
              d="M 0 0 L 65 -38 A 75 75 0 1 1 -74 13 Z"
              fill="#2563EB"
            />

            {/* Slice 2: Cyan (Western) - ~25% of the pie */}
            {/* Path from -110 deg to -30 deg */}
            <path
              d="M 0 0 L -25 -71 A 75 75 0 0 1 65 -38 Z"
              fill="#00C6FF"
            />

            {/* Slice 3: Yellow/Orange (Reserve) - ~20% of the pie */}
            {/* Path from 170 deg to 250 deg (-110 deg) */}
            <path
              d="M 0 0 L -74 13 A 75 75 0 0 1 -25 -71 Z"
              fill="#F59E0B"
            />

            {/* Inner accent ring */}
            <circle cx="0" cy="0" r="12" fill="#FFFFFF" />
          </g>
        </svg>
      </div>
    </div>
  );
}
