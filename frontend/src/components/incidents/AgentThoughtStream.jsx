/**
 * src/components/incidents/AgentThoughtStream.jsx
 * Owner: Developer 4 (Frontend)
 *
 * Real-time, explainable Agent Thought & Tool Execution Visualizer.
 * Renders the multi-step observe -> think -> act -> observe reasoning loop
 * with live pulse status and formatted parameter cards.
 */
import { useState } from "react";

export default function AgentThoughtStream({ auditLogs = [], isRunning = false, incidentStatus = "INVESTIGATING" }) {
  const [expandedStep, setExpandedStep] = useState(null);

  // Filter logs that belong to agent reasoning steps (step_index or tool calls)
  const steps = (auditLogs || []).filter(
    (log) => log.tool || log.step_index !== undefined || log.thought || (log.action && log.action.includes("Step"))
  );

  const isResolved = incidentStatus === "RESOLVED";
  const isEscalated = incidentStatus === "WAITING_APPROVAL";

  return (
    <div className="panel elevated-panel" style={{ marginTop: 16, background: "rgba(7, 30, 42, 0.7)", border: "1px solid rgba(35, 184, 201, 0.25)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, borderBottom: "1px solid rgba(255, 255, 255, 0.08)", paddingBottom: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 18 }}>🧠</span>
          <div>
            <h3 style={{ margin: 0, fontSize: 14, fontFamily: "Space Grotesk", color: "#ffffff", letterSpacing: "0.02em" }}>
              Autonomous Agent Thought Stream
            </h3>
            <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
              Live multi-step reasoning, tool dispatch, and environment observations
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {isRunning ? (
            <span style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#23B8C9", fontWeight: 600, background: "rgba(35, 184, 201, 0.15)", padding: "3px 8px", borderRadius: 12 }}>
              <span className="loading-orb" style={{ width: 8, height: 8 }} />
              THINKING & EXECUTING…
            </span>
          ) : isResolved ? (
            <span style={{ fontSize: 11, color: "#10B981", fontWeight: 600, background: "rgba(16, 185, 129, 0.15)", padding: "3px 8px", borderRadius: 12 }}>
              ✓ AUTONOMOUSLY RESOLVED
            </span>
          ) : isEscalated ? (
            <span style={{ fontSize: 11, color: "#F59E0B", fontWeight: 600, background: "rgba(245, 158, 11, 0.15)", padding: "3px 8px", borderRadius: 12 }}>
              ⚠️ ESCALATED FOR APPROVAL
            </span>
          ) : (
            <span style={{ fontSize: 11, color: "var(--text-secondary)", background: "rgba(255, 255, 255, 0.05)", padding: "3px 8px", borderRadius: 12 }}>
              READY
            </span>
          )}
        </div>
      </div>

      {steps.length === 0 ? (
        <div style={{ padding: "20px 0", textAlign: "center", color: "var(--text-secondary)", fontSize: 13 }}>
          No reasoning steps recorded yet. Click <strong>"▶ Trigger Agent"</strong> to start the autonomous loop.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {steps.map((step, idx) => {
            const stepNum = step.step_index !== undefined ? step.step_index : idx + 1;
            const hasDetails = step.tool_args || step.calculations_performed || step.data_sources_checked;
            const isExpanded = expandedStep === idx;

            return (
              <div
                key={idx}
                style={{
                  background: "rgba(13, 22, 33, 0.7)",
                  border: "1px solid rgba(255, 255, 255, 0.07)",
                  borderRadius: 8,
                  padding: "12px 14px",
                  transition: "all 0.15s ease",
                }}
              >
                {/* Step Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, background: "rgba(35, 184, 201, 0.2)", color: "#23B8C9", padding: "2px 6px", borderRadius: 4, fontFamily: "JetBrains Mono" }}>
                      STEP {stepNum}
                    </span>
                    {step.tool && (
                      <span style={{ fontSize: 12, fontWeight: 600, color: "#E0F2FE", fontFamily: "JetBrains Mono" }}>
                        🛠️ {step.tool}()
                      </span>
                    )}
                  </div>
                  <span style={{ fontSize: 11, color: "var(--text-secondary)", fontFamily: "JetBrains Mono" }}>
                    {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ""}
                  </span>
                </div>

                {/* Agent Thought / Reasoning */}
                {(step.thought || step.reason) && (
                  <div style={{ marginBottom: 6, fontSize: 12.5, color: "#93C5FD", lineHeight: 1.5, background: "rgba(59, 130, 246, 0.08)", padding: "6px 10px", borderRadius: 6, borderLeft: "2px solid #3B82F6" }}>
                    <strong style={{ color: "#60A5FA", fontSize: 11, textTransform: "uppercase", display: "block", marginBottom: 2 }}>
                      🧠 Agent Reasoning
                    </strong>
                    {step.thought || step.reason}
                  </div>
                )}

                {/* Observation / Tool Result */}
                {step.result && (
                  <div style={{ fontSize: 12.5, color: "#E2E8F0", lineHeight: 1.5, background: "rgba(16, 185, 129, 0.06)", padding: "6px 10px", borderRadius: 6, borderLeft: "2px solid #10B981" }}>
                    <strong style={{ color: "#34D399", fontSize: 11, textTransform: "uppercase", display: "block", marginBottom: 2 }}>
                      👁️ Environment Observation
                    </strong>
                    {step.result}
                  </div>
                )}

                {/* Tool Details / Calculations Toggle */}
                {hasDetails && (
                  <div style={{ marginTop: 6 }}>
                    <button
                      onClick={() => setExpandedStep(isExpanded ? null : idx)}
                      style={{ background: "none", border: "none", color: "#23B8C9", fontSize: 11, cursor: "pointer", padding: 0, display: "flex", alignItems: "center", gap: 4 }}
                    >
                      {isExpanded ? "▾ Hide Tool Parameters & Math" : "▸ View Tool Parameters & Math"}
                    </button>

                    {isExpanded && (
                      <div style={{ marginTop: 8, padding: 8, background: "rgba(0, 0, 0, 0.4)", borderRadius: 6, fontSize: 11, fontFamily: "JetBrains Mono", color: "#A7F3D0" }}>
                        {step.tool_args && (
                          <div style={{ marginBottom: 4 }}>
                            <span style={{ color: "#94A3B8" }}>Input Arguments: </span>
                            {JSON.stringify(step.tool_args, null, 2)}
                          </div>
                        )}
                        {step.calculations_performed && (
                          <div>
                            <span style={{ color: "#94A3B8" }}>Calculations: </span>
                            {JSON.stringify(step.calculations_performed, null, 2)}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
