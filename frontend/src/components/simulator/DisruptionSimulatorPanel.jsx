/**
 * src/components/simulator/DisruptionSimulatorPanel.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Team doc Section 18: buttons to inject demo disruptions.
 * RECEIVES: click events
 * DELIVERS: POST /simulator/inject (src/api/simulator.js) -> new Incident
 */
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

  const handleInject = async (scenario) => {
    try {
      const incident = await injectScenario(scenario);
      // TODO (Dev4): also call POST /agent/trigger here once agent_loop.py works,
      // so the demo doesn't require a separate manual "trigger" click.
      navigate(`/incidents/${incident.incident_id}`);
    } catch (err) {
      console.error("Injection failed:", err);
    }
  };

  return (
    <div className="panel">
      <h2>Disruption Simulator</h2>
      <p style={{ color: "var(--text-secondary)" }}>For demo/testing only — not shown to end customers.</p>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {SCENARIOS.map((s) => (
          <button key={s.key} onClick={() => handleInject(s.key)}>{s.label}</button>
        ))}
      </div>
    </div>
  );
}
