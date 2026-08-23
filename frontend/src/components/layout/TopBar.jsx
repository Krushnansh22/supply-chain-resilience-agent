/**
 * src/components/layout/TopBar.jsx
 * Owner: Developer 4 (Frontend)
 * Header with Global Autonomous Agent Controller and Environment Scanner.
 */
import { useEffect, useState } from "react";
import { apiRequest } from "../../api/client.js";
import { processBacklog, scanAndTriage, getSystemStatus } from "../../api/agent.js";

export default function TopBar() {
  const [online, setOnline] = useState(null);
  const [running, setRunning] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  const fetchStatus = () => {
    apiRequest("/health")
      .then(() => {
        setOnline(true);
        getSystemStatus().then(setSystemStatus).catch(() => null);
      })
      .catch(() => setOnline(false));
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleStartAgent = async () => {
    setRunning(true);
    setFeedback(null);
    try {
      // Run the global autonomous agent queue processor
      const res = await processBacklog();
      setFeedback(res.message || "Agent operations completed.");
      fetchStatus();
      setTimeout(() => setFeedback(null), 7000);
    } catch (err) {
      console.error("Agent execution error:", err);
      setFeedback("Failed to complete agent cycle.");
      setTimeout(() => setFeedback(null), 5000);
    } finally {
      setRunning(false);
    }
  };

  const statusColor = online === null ? "#667085" : online ? "#16A46B" : "#D94B5B";
  const statusLabel = online === null ? "CHECKING" : online ? "LIVE" : "OFFLINE";

  return (
    <header className="header-top">
      <div className="header-top-inner">
        <div className="header-logo">
          <div
            className="mark"
            style={{
              width: 30,
              height: 30,
              borderRadius: 6,
              background: "linear-gradient(135deg, #073F46 0%, #07535A 35%, #23B8C9 65%, #E5A11A 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#ffffff",
              fontSize: 11,
              fontWeight: 700,
            }}
          />
          <span
            className="name"
            style={{ fontFamily: "Space Grotesk", fontSize: 13, fontWeight: 700, color: "#ffffff" }}
          >
            Supply Chain Disruption Control Agent
          </span>
        </div>
        <span
          className="header-title"
          style={{ fontFamily: "Space Grotesk", fontSize: 13, fontWeight: 600, color: "#ffffff" }}
        >
          HOP 2026 // Team TRACE
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        {/* Global Autonomous Agent Controller Button */}
        <button
          onClick={handleStartAgent}
          disabled={running}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            background: running ? "rgba(35, 184, 201, 0.25)" : "linear-gradient(135deg, #073F46, #07535A)",
            border: "1px solid rgba(35, 184, 201, 0.5)",
            color: "#23B8C9",
            padding: "6px 14px",
            borderRadius: 6,
            fontSize: 12,
            fontWeight: 600,
            cursor: running ? "not-allowed" : "pointer",
            fontFamily: "Space Grotesk",
            transition: "all 0.15s ease",
            boxShadow: running ? "0 0 12px rgba(35, 184, 201, 0.4)" : "none",
          }}
        >
          <span style={{ fontSize: 13 }}>{running ? "⚙️" : "⚡"}</span>
          {running ? "Agent Processing Queue…" : "Start Autonomous Agent"}
        </button>

        {/* Backend & Agent Status Indicator */}
        <div className="header-status" style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span className="status-dot-sm" style={{ background: running ? "#23B8C9" : statusColor, width: 6, height: 6, borderRadius: "50%" }} />
          <span
            className="status-text"
            style={{ fontFamily: "JetBrains Mono", fontSize: 10, color: running ? "#23B8C9" : statusColor, letterSpacing: "0.05em" }}
          >
            {running ? "PROCESSING" : statusLabel}
          </span>
        </div>
      </div>

      {feedback && (
        <div
          style={{
            position: "fixed",
            top: 60,
            right: 24,
            zIndex: 9999,
            background: "#073F46",
            border: "1px solid #23B8C9",
            color: "#ffffff",
            padding: "10px 16px",
            borderRadius: 8,
            boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
            fontSize: 12.5,
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <span>🎯</span>
          <span>{feedback}</span>
        </div>
      )}
    </header>
  );
}