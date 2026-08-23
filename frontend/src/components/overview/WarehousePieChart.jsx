import { useState } from "react";

const WAREHOUSE_DATA = {
  western: {
    name: "Western Hub",
    color: "#00C6FF",
    share: "25%",
    utilization: "78%",
    capacity: "45,000 units",
    activeShipments: 14,
    status: "Optimal",
  },
  central: {
    name: "Central Logistics Center",
    color: "#2563EB",
    share: "55%",
    utilization: "92%",
    capacity: "120,000 units",
    activeShipments: 38,
    status: "High Load",
  },
  reserve: {
    name: "Reserve Buffer Facility",
    color: "#F59E0B",
    share: "20%",
    utilization: "34%",
    capacity: "30,000 units",
    activeShipments: 6,
    status: "Standby",
  },
};

export default function WarehousePieChart() {
  const [selectedKey, setSelectedKey] = useState("central");
  const current = WAREHOUSE_DATA[selectedKey];

  return (
    <div className="dashboard-card" style={{ position: "relative" }}>
      {/* Header */}
      <div className="card-header-row">
        <div>
          <span className="card-header-title">Warehouse Workload</span>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", marginLeft: "8px" }}>
            (Click legend or slice)
          </span>
        </div>
        <div className="card-header-actions">
          <button
            className="action-icon-btn"
            title="Reset view"
            onClick={() => setSelectedKey("central")}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 4v6h-6M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Interactive Callout Legend Pills */}
      <div style={{ display: "flex", gap: "10px", margin: "12px 0 4px", justifyContent: "center" }}>
        <button
          onClick={() => setSelectedKey("western")}
          className="chart-callout-pill cyan"
          style={{
            cursor: "pointer",
            border: selectedKey === "western" ? "2px solid #00C6FF" : "1px solid transparent",
            transform: selectedKey === "western" ? "scale(1.08)" : "scale(1)",
            transition: "all 0.15s ease",
            boxShadow: selectedKey === "western" ? "0 0 10px rgba(0, 198, 255, 0.4)" : "none",
          }}
        >
          Western ({WAREHOUSE_DATA.western.share})
        </button>

        <button
          onClick={() => setSelectedKey("central")}
          className="chart-callout-pill blue"
          style={{
            cursor: "pointer",
            border: selectedKey === "central" ? "2px solid #2563EB" : "1px solid transparent",
            transform: selectedKey === "central" ? "scale(1.08)" : "scale(1)",
            transition: "all 0.15s ease",
            boxShadow: selectedKey === "central" ? "0 0 10px rgba(37, 99, 235, 0.4)" : "none",
          }}
        >
          Central ({WAREHOUSE_DATA.central.share})
        </button>

        <button
          onClick={() => setSelectedKey("reserve")}
          className="chart-callout-pill yellow"
          style={{
            cursor: "pointer",
            border: selectedKey === "reserve" ? "2px solid #F59E0B" : "1px solid transparent",
            transform: selectedKey === "reserve" ? "scale(1.08)" : "scale(1)",
            transition: "all 0.15s ease",
            boxShadow: selectedKey === "reserve" ? "0 0 10px rgba(245, 158, 11, 0.4)" : "none",
          }}
        >
          Reserve ({WAREHOUSE_DATA.reserve.share})
        </button>
      </div>

      {/* SVG Pie Chart Graphic */}
      <div className="pie-chart-container" style={{ position: "relative", minHeight: 200 }}>
        <svg viewBox="0 0 320 240" width="100%" height="100%" style={{ overflow: "visible" }}>
          {/* Connecting Lines */}
          <polyline
            points="65,40 115,40 140,85"
            fill="none"
            stroke="#00C6FF"
            strokeWidth={selectedKey === "western" ? "3" : "1.5"}
            strokeOpacity={selectedKey === "western" ? "1" : "0.4"}
          />
          <polyline
            points="245,95 210,95 185,120"
            fill="none"
            stroke="#2563EB"
            strokeWidth={selectedKey === "central" ? "3" : "1.5"}
            strokeOpacity={selectedKey === "central" ? "1" : "0.4"}
          />
          <polyline
            points="70,185 110,185 130,160"
            fill="none"
            stroke="#F59E0B"
            strokeWidth={selectedKey === "reserve" ? "3" : "1.5"}
            strokeOpacity={selectedKey === "reserve" ? "1" : "0.4"}
          />

          {/* Pie Chart Group (Center: 160, 125, Radius: 75) */}
          <g transform="translate(160, 125)">
            {/* Slice 1: Central (Blue) */}
            <path
              d="M 0 0 L 65 -38 A 75 75 0 1 1 -74 13 Z"
              fill="#2563EB"
              style={{
                cursor: "pointer",
                opacity: selectedKey === "central" ? 1 : 0.65,
                transform: selectedKey === "central" ? "scale(1.06)" : "scale(1)",
                transition: "all 0.2s ease",
              }}
              onClick={() => setSelectedKey("central")}
            />

            {/* Slice 2: Western (Cyan) */}
            <path
              d="M 0 0 L -25 -71 A 75 75 0 0 1 65 -38 Z"
              fill="#00C6FF"
              style={{
                cursor: "pointer",
                opacity: selectedKey === "western" ? 1 : 0.65,
                transform: selectedKey === "western" ? "scale(1.06)" : "scale(1)",
                transition: "all 0.2s ease",
              }}
              onClick={() => setSelectedKey("western")}
            />

            {/* Slice 3: Reserve (Yellow) */}
            <path
              d="M 0 0 L -74 13 A 75 75 0 0 1 -25 -71 Z"
              fill="#F59E0B"
              style={{
                cursor: "pointer",
                opacity: selectedKey === "reserve" ? 1 : 0.65,
                transform: selectedKey === "reserve" ? "scale(1.06)" : "scale(1)",
                transition: "all 0.2s ease",
              }}
              onClick={() => setSelectedKey("reserve")}
            />

            {/* Inner accent circle */}
            <circle cx="0" cy="0" r="14" fill="#FFFFFF" />
          </g>
        </svg>
      </div>

      {/* Selected Segment Breakdown Metrics Box */}
      <div
        style={{
          marginTop: "10px",
          padding: "12px 16px",
          background: "var(--bg-canvas, #F8FAFC)",
          borderRadius: "var(--radius-md, 12px)",
          border: `1px solid ${current.color}40`,
          borderLeft: `4px solid ${current.color}`,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
          <span style={{ fontWeight: 700, fontSize: "13px", color: "var(--text-primary)" }}>
            {current.name}
          </span>
          <span
            style={{
              fontSize: "11px",
              fontWeight: 700,
              padding: "2px 8px",
              borderRadius: "6px",
              background: `${current.color}20`,
              color: current.color,
            }}
          >
            {current.status}
          </span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "8px", fontSize: "12px" }}>
          <div>
            <span style={{ color: "var(--text-muted)", fontSize: "10px" }}>Workload Share</span>
            <div style={{ fontWeight: 700, color: "var(--text-primary)" }}>{current.share}</div>
          </div>
          <div>
            <span style={{ color: "var(--text-muted)", fontSize: "10px" }}>Capacity Usage</span>
            <div style={{ fontWeight: 700, color: "var(--text-primary)" }}>{current.utilization}</div>
          </div>
          <div>
            <span style={{ color: "var(--text-muted)", fontSize: "10px" }}>Active Shipments</span>
            <div style={{ fontWeight: 700, color: "var(--text-primary)" }}>{current.activeShipments}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
