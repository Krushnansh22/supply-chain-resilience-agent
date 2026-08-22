/**
 * src/components/layout/TopBar.jsx
 * Owner: Developer 4 (Frontend)
 * Fixed header matching screenshot specification.
 * Rounded glass container, thin translucent border, gradient logo.
 * "Supply Chain Disruption Control Agent" / "HOP 2026 // Team TRACE".
 * Online/offline status on right. Backend API integration preserved.
 */

import { useEffect, useState } from "react";
import { apiRequest } from "../../api/client.js";

export default function TopBar() {
  const [online, setOnline] = useState(null); // null = checking, true/false = known

  useEffect(() => {
    const check = () => apiRequest("/health").then(() => setOnline(true)).catch(() => setOnline(false));
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  const statusColor = online === null ? "#667085" : online ? "#16A46B" : "#D94B5B";
  const statusLabel = online === null ? "CHECKING" : online ? "LIVE" : "OFFLINE";

  return (
    <header className="header-top">
      <div className="header-top-inner">
        <div className="header-logo">
          <div className="mark"
            style={{
              width: 30, height: 30,
              borderRadius: 6,
              background: "linear-gradient(135deg, #073F46 0%, #07535A 35%, #23B8C9 65%, #E5A11A 100%)",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#ffffff", fontSize: 11, fontWeight: 700,
            }}
          />
          <span className="name"
            style={{ fontFamily: "Space Grotesk", fontSize: 13, fontWeight: 700, color: "#ffffff" }}>
            Supply Chain Disruption Control Agent
          </span>
        </div>
        <span className="header-title"
          style={{ fontFamily: "Space Grotesk", fontSize: 13, fontWeight: 600, color: "#ffffff" }}>
          HOP 2026 // Team TRACE
        </span>
      </div>

      <div className="header-status">
        <span className="status-dot-sm"
          style={{ background: statusColor, width: 5, height: 5 }} />
        <span className="status-text"
          style={{ fontFamily: "JetBrains Mono", fontSize: 10, color: statusColor, letterSpacing: "0.05em" }}>
          {statusLabel}
        </span>
      </div>
    </header>
  );
}