/**
 * src/components/layout/TopBar.jsx
 * Owner: Developer 4 (Frontend)
 * Placeholder header. TODO: show connection status to backend (ping /health).
 */
export default function TopBar() {
  return (
    <header className="panel" style={{ borderRadius: 0, borderLeft: "none", borderTop: "none", borderRight: "none" }}>
      <strong>Supply Chain Disruption Control Agent</strong>
      <span style={{ color: "var(--text-muted)", marginLeft: 12, fontFamily: "var(--font-mono)", fontSize: 12 }}>
        HOP 2026 // Team TRACE
      </span>
    </header>
  );
}
