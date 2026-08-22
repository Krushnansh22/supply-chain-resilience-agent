/**
 * src/components/overview/WarehouseLineChart.jsx
 * Exact visual match to the multi-line chart card in the reference screenshot:
 *  - Y-axis: 200, 150, 100, 50, 0
 *  - X-axis: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11
 *  - Vertical dashed grid lines
 *  - 3 curved lines: Raw material (Red), Product deliveries (Green), Warehouse load (Yellow)
 *  - Legend at the bottom
 */

export default function WarehouseLineChart() {
  const xLabels = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11"];
  const yLabels = [200, 150, 100, 50, 0];

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

      {/* SVG Multi-Line Chart */}
      <div className="line-chart-container">
        <svg viewBox="0 0 540 200" width="100%" height="100%" preserveAspectRatio="none">
          {/* Y-Axis Labels */}
          {yLabels.map((val, idx) => {
            const y = 20 + idx * 36;
            return (
              <text
                key={val}
                x="20"
                y={y + 4}
                fill="#94A3B8"
                fontSize="11"
                fontFamily="Inter, sans-serif"
                fontWeight="500"
                textAnchor="end"
              >
                {val}
              </text>
            );
          })}

          {/* Vertical dashed grid lines & X-axis labels */}
          {xLabels.map((lbl, idx) => {
            const x = 50 + idx * 47;
            return (
              <g key={lbl}>
                {/* Dashed vertical line */}
                <line
                  x1={x}
                  y1={15}
                  x2={x}
                  y2={164}
                  stroke="#E2E8F0"
                  strokeWidth="1"
                  strokeDasharray="3 3"
                />
                {/* X-axis label */}
                <text
                  x={x}
                  y={184}
                  fill="#94A3B8"
                  fontSize="11"
                  fontFamily="Inter, sans-serif"
                  fontWeight="500"
                  textAnchor="middle"
                >
                  {lbl}
                </text>
              </g>
            );
          })}

          {/* Bottom baseline */}
          <line x1="45" y1="164" x2="530" y2="164" stroke="#E2E8F0" strokeWidth="1" />

          {/* Line 1: Yellow - "Warehouse load" */}
          <path
            d="M 50,164 Q 75,100 97,105 T 144,115 T 191,135 T 238,148 T 285,160 T 332,168 T 379,155 T 426,148 T 473,135 T 520,105"
            fill="none"
            stroke="#F59E0B"
            strokeWidth="2.4"
            strokeLinecap="round"
          />

          {/* Line 2: Green - "Product deliveries" */}
          <path
            d="M 50,164 Q 75,160 97,150 T 144,160 T 191,150 T 238,140 T 285,130 T 332,145 T 379,135 T 426,130 T 473,115 T 520,135"
            fill="none"
            stroke="#10B981"
            strokeWidth="2.4"
            strokeLinecap="round"
          />

          {/* Line 3: Red - "Raw material" */}
          <path
            d="M 50,164 Q 75,135 97,140 T 144,155 T 191,145 T 238,130 T 285,115 T 332,140 T 379,150 T 426,155 T 473,110 T 520,100"
            fill="none"
            stroke="#EF4444"
            strokeWidth="2.4"
            strokeLinecap="round"
          />
        </svg>
      </div>

      {/* Legend */}
      <div className="line-chart-legend">
        <div className="legend-item">
          <span className="legend-dot red" />
          <span>Raw material</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot green" />
          <span>Product deliveries</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot yellow" />
          <span>Warehouse load</span>
        </div>
      </div>
    </div>
  );
}
