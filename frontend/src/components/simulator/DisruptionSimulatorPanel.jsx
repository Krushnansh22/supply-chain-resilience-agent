/**
 * src/components/simulator/DisruptionSimulatorPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 18: buttons to inject demo disruptions.
 * RECEIVES: click events
 * DELIVERS: POST /simulator/inject (src/api/simulator.js) -> new Incident
 */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { injectScenario } from "../../api/simulator.js";

const SCENARIOS = [
  { key: "SUPPLIER_DELAY", label: "Inject Supplier Delay" },
  { key: "STALE_INVENTORY", label: "Inject Stale Inventory" },
  { key: "SUPPLIER_LIE", label: "Inject Supplier Lie" },
  { key: "QUALITY_FAILURE", label: "Inject Quality Failure" },
  { key: "BUDGET_OVERRUN", label: "Inject Budget Overrun" },
];

export default function DisruptionSimulatorPanel() {
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [injecting, setInjecting] = useState(null);

  const handleInject = async (scenario) => {
    setInjecting(scenario);
    setError(null);
    try {
      const incident = await injectScenario(scenario);
      // TODO (Dev4): also call POST /agent/trigger here once agent_loop.py works,
      // so the demo doesn't require a separate manual "trigger" click.
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
          <div className="page-subtitle">For demo/testing only — not shown to end customers. Injecting creates a real incident and jumps to its Command Center.</div>
        </div>
      </div>
      <div className="panel">
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {SCENARIOS.map((s) => (
            <button key={s.key} className="btn-primary" disabled={!!injecting} onClick={() => handleInject(s.key)}>
              {injecting === s.key ? "Injecting…" : s.label}
            </button>
          ))}
        </div>
        {error && <div className="error-banner">{error}</div>}
      </div>
    </div>
  );
}
