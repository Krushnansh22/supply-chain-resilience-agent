/**
 * src/components/layout/TopBar.jsx
 * Owner: Developer 4 (Frontend)
 * Header with a live backend connection indicator, pinging GET /health
 * (app/main.py) so judges can see at a glance if the API is reachable.
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

  const statusColor = online === null ? "var(--text-muted)" : online ? "var(--status-low)" : "var(--status-critical)";
  const statusLabel = online === null ? "CHECKING" : online ? "LIVE" : "OFFLINE";

  return (
    <header
      className="panel"
      style={{
        borderRadius: 0,
        borderLeft: "none",
        borderTop: "none",
        borderRight: "none",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}
    >
      <div>
        <strong>Supply Chain Disruption Control Agent</strong>
        <span style={{ color: "var(--text-muted)", marginLeft: 12, fontFamily: "var(--font-mono)", fontSize: 12 }}>
          HOP 2026 // Team TRACE
        </span>
      </div>
      <span style={{ display: "flex", alignItems: "center", gap: 6, color: statusColor, fontSize: 12, fontFamily: "var(--font-mono)" }}>
        <span style={{ width: 8, height: 8, borderRadius: "50%", background: statusColor, display: "inline-block" }} />
        {statusLabel}
      </span>
    </header>
  );
}
