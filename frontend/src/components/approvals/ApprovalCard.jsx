/**
 * src/components/approvals/ApprovalCard.jsx
 * Owner: Developer 4 (Frontend)
 *
 * RECEIVES: `plan`, optional `incident`
 * DELIVERS: POST /agent/approve (with optional revised_value for broken data) or /agent/reject
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import { approvePlan, rejectPlan } from "../../api/agent.js";
import SeverityBadge from "../common/SeverityBadge.jsx";

export default function ApprovalCard({ plan, incident, onDecided }) {
  const [pending, setPending] = useState(null);
  const [error, setError] = useState(null);
  const [revisedValue, setRevisedValue] = useState("");
  const [revisionReason, setRevisionReason] = useState("");

  if (!plan) return null;

  const options = plan.options || [];
  const recommended = options.find((o) => o.option_id === plan.recommended_option_id);
  const alternatives = options.filter((o) => o.option_id !== plan.recommended_option_id);
  const targetIncidentId = plan.incident_id || incident?.incident_id;

  const isDataInconsistency =
    incident?.type === "STALE_INVENTORY" ||
    incident?.status === "DATA_INCONSISTENCY" ||
    incident?.data_inconsistency_detected ||
    plan?.trigger_criterion === "DATA_INCONSISTENCY" ||
    (plan?.recommendation_reason && plan.recommendation_reason.toLowerCase().includes("physical count"));

  const isStockValid = revisedValue.trim() !== "" && !isNaN(Number(revisedValue)) && Number(revisedValue) >= 0;
  const isNegativeEntered = revisedValue.trim() !== "" && Number(revisedValue) < 0;

  const handleDecision = async (action) => {
    setPending(action);
    setError(null);
    try {
      if (action === "approve") {
        if (isDataInconsistency && !isStockValid) {
          setError("Please enter a valid non-negative physical stock count (>= 0).");
          setPending(null);
          return;
        }
        await approvePlan(
          targetIncidentId,
          isDataInconsistency && revisedValue !== "" ? Number(revisedValue) : null,
          revisionReason || "Physical stock count verification"
        );
      } else {
        await rejectPlan(targetIncidentId);
      }
      onDecided?.(action);
    } catch (err) {
      setError(err.message || `Failed to ${action} plan.`);
    } finally {
      setPending(null);
    }
  };

  const recCost = recommended?.total_cost ?? 0;
  const threshold = plan.approval_threshold_usd ?? 50000;
  const diffCost = Math.max(0, recCost - threshold);

  return (
    <div className="panel approval-glow">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, flexWrap: "wrap" }}>
        <div>
          <h3 style={{ marginBottom: 4 }}>
            {incident ? (
              <Link to={`/incidents/${incident.incident_id}`} style={{ color: "inherit", textDecoration: "none" }}>
                {incident.incident_id}
              </Link>
            ) : (
              targetIncidentId
            )}
            {incident?.severity && <span style={{ marginLeft: 8 }}><SeverityBadge severity={incident.severity} /></span>}
          </h3>
          {incident && (
            <div style={{ color: "var(--text-secondary)", fontSize: 13 }}>
              {String(incident.type || "").replaceAll("_", " ")} · Component {incident.affected_component || "—"} · PO {incident.affected_po || "—"}
            </div>
          )}
        </div>
        <span className={isDataInconsistency ? "badge badge-critical" : "badge badge-high"}>
          {isDataInconsistency ? "DATA CORRECTION REQUIRED" : "APPROVAL REQUIRED"}
        </span>
      </div>

      {isDataInconsistency ? (
        /* Data Inconsistency / Broken Data Correction Form */
        <div style={{ marginTop: 14, background: "rgba(245, 158, 11, 0.08)", border: "1px solid rgba(245, 158, 11, 0.3)", borderRadius: 8, padding: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <span style={{ fontSize: 16 }}>⚠️</span>
            <strong style={{ fontSize: 13, color: "var(--text-primary)" }}>
              Data Discrepancy Detected — Component {incident?.affected_component || "COMP-104"}
            </strong>
          </div>
          <p style={{ fontSize: 12.5, color: "var(--text-secondary)", margin: "0 0 12px 0", lineHeight: 1.5 }}>
            The agent identified broken/stale or negative stock values in the system of record.
            Please enter the verified physical stock count below. Submitting will update the database baseline and proceed with calibrated planning.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
            <div>
              <label style={{ display: "block", fontSize: 11, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4, textTransform: "uppercase" }}>
                Revised Physical Stock Count (Usable Units) *
              </label>
              <input
                type="number"
                min="0"
                className="input-field"
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  background: "var(--bg-card)",
                  border: isNegativeEntered
                    ? "1px solid #EF4444"
                    : (isStockValid ? "1px solid #10B981" : "1px solid var(--border-subtle)"),
                  borderRadius: 6,
                  color: "var(--text-primary)",
                  fontSize: 13,
                }}
                placeholder="e.g. 250"
                value={revisedValue}
                onChange={(e) => setRevisedValue(e.target.value)}
              />
              {isNegativeEntered && (
                <div style={{ color: "#EF4444", fontSize: 11, marginTop: 4 }}>
                  Stock amount cannot be negative. Must be 0 or higher.
                </div>
              )}
            </div>
            <div>
              <label style={{ display: "block", fontSize: 11, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4, textTransform: "uppercase" }}>
                Correction Reason / Audit Note
              </label>
              <input
                type="text"
                className="input-field"
                style={{ width: "100%", padding: "8px 12px", background: "var(--bg-card)", border: "1px solid var(--border-subtle)", borderRadius: 6, color: "var(--text-primary)", fontSize: 13 }}
                placeholder="e.g. Warehouse physical recount"
                value={revisionReason}
                onChange={(e) => setRevisionReason(e.target.value)}
              />
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="approval-cost-grid">
            <div className="approval-cost-item">
              <div className="kpi-label" style={{ fontSize: 11 }}>ESTIMATED COST</div>
              <div className="kpi-value-sm">{recCost > 0 ? `$${recCost.toLocaleString()}` : "Pending Quote"}</div>
            </div>
            <div className="approval-cost-item">
              <div className="kpi-label" style={{ fontSize: 11 }}>APPROVAL THRESHOLD</div>
              <div className="kpi-value-sm">${threshold.toLocaleString()}</div>
            </div>
            <div className="approval-cost-item">
              <div className="kpi-label" style={{ fontSize: 11 }}>DELIVERY</div>
              <div className="kpi-value-sm">{recommended?.max_delivery_days ? `${recommended.max_delivery_days}d` : "—"}</div>
            </div>
          </div>

          <p style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 14 }}>
            <strong style={{ color: "var(--text-primary)" }}>Why approval is required: </strong>
            {(() => {
              const brief = incident?.decision_brief || incident?.escalation_reason || plan?.decision_brief;
              if (recCost > threshold) {
                return `This plan costs $${recCost.toLocaleString()} and exceeds the $${threshold.toLocaleString()} autonomous-execution limit by $${diffCost.toLocaleString()}.`;
              }
              if (brief && !brief.toLowerCase().includes("no recovery plan")) {
                return brief;
              }
              if (recCost > 0) {
                return `Recovery plan costs $${recCost.toLocaleString()} and requires coordinator authorization before ERP order execution.`;
              }
              return "Critical disruption escalated: Candidate supplier lead times or capacity exceed buffer limits. Coordinator intervention required.";
            })()}
          </p>
        </>
      )}

      {plan.recommendation_reason && (
        <p style={{ fontSize: 13, marginTop: 10 }}>
          <strong>Recommendation: </strong>
          <span style={{ color: "var(--text-secondary)" }}>{plan.recommendation_reason}</span>
        </p>
      )}

      {alternatives.length > 0 && !isDataInconsistency && (
        <div style={{ marginTop: 8 }}>
          <div className="kpi-label" style={{ fontSize: 11, marginBottom: 4 }}>ALTERNATIVES CONSIDERED</div>
          {alternatives.map((opt) => (
            <div key={opt.option_id} className="plan-option-alloc" style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 6, marginTop: 4 }}>
              <strong>Option {opt.option_id}</strong> — ${(opt.total_cost ?? 0).toLocaleString()}, {opt.max_delivery_days}d{" "}
              {opt.constraints_satisfied ? (
                <span className="badge badge-low">VALID</span>
              ) : (
                <span className="badge badge-critical">REJECTED{opt.rejection_reason ? `: ${opt.rejection_reason}` : ""}</span>
              )}
            </div>
          ))}
        </div>
      )}

      {error && <div className="error-banner" style={{ marginTop: 10 }}>{error}</div>}

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <button
          className="btn-approve"
          disabled={!!pending || (isDataInconsistency && !isStockValid)}
          onClick={() => handleDecision("approve")}
        >
          {pending === "approve"
            ? "Updating & Approving…"
            : (isDataInconsistency ? "✓ Submit Revised Data & Approve" : "✓ Approve Plan")}
        </button>
        <button className="btn-reject" disabled={!!pending} onClick={() => handleDecision("reject")}>
          {pending === "reject" ? "Rejecting…" : "✕ Reject"}
        </button>
      </div>
    </div>
  );
}