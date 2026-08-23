/**
 * src/components/simulator/DisruptionSimulatorPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * DELIVERS: POST /simulator/inject -> new Incident
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { injectScenario } from "../../api/simulator.js";

const SCENARIOS = [
  { key: "SUPPLIER_DELAY", label: "Supplier Delay" },
  { key: "STALE_INVENTORY", label: "Stale Inventory" },
  { key: "SUPPLIER_LIE", label: "Supplier Lie" },
  { key: "QUALITY_FAILURE", label: "Quality Failure" },
  { key: "BUDGET_OVERRUN", label: "Budget Overrun" },
];

export default function DisruptionSimulatorPanel() {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [injecting, setInjecting] = useState(null);
  const [lastIncident, setLastIncident] = useState(null);

  const handleInject = async (scenario) => {
    setInjecting(scenario);
    setError(null);
    try {
      const incident = await injectScenario(scenario);
      navigate(`/incidents/${incident.incident_id}`);
    } catch (err) {
      setError(err.message || "Failed to inject scenario.");
    } finally {
      setInjecting(null);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Disruption Simulator</h1>
          <div className="page-subtitle">For demo/testing only. Injecting creates a real incident and jumps to its Command Center.</div>
        </div>
      </div>
      <div className="panel elevated-panel">
        <div className="scenario-grid">
          {SCENARIOS.map((s) => (
            <button
              key={s.key}
              className="btn-primary scenario-btn"
              disabled={!!injecting}
              onClick={() => handleInject(s.key)}
            >
              <span className="scenario-btn-icon">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" /></svg>
              </span>
              {injecting === s.key ? "Injecting…" : s.label}
            </button>
          ))}
        </div>
        {lastIncident && (
          <div style={{ marginTop: 16, color: "var(--text-secondary)", fontSize: 13 }}>
            Agent investigation started for{" "}
            <Link to={`/incidents/${lastIncident.incident_id}`}>{lastIncident.incident_id}</Link>.
            {" "}Follow progress in <Link to="/agent-activity">Agent Activity</Link>.
          </div>
        )}
        {error && <div className="error-banner">{error}</div>}
      </div>
    </div>
  );
}