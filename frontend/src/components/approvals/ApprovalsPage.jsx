import { useEffect, useState } from "react";
import { listIncidents } from "../../api/incidents.js";
import { getAgentPlan } from "../../api/agent.js";
import ApprovalCard from "./ApprovalCard.jsx";

const FALLBACK_APPROVALS = [
  {
    incident: {
      incident_id: "INC-011",
      severity: "CRITICAL",
      type: "DELIVERY_BREACH",
      affected_component: "CMP-004",
      affected_po: "PO-001",
      status: "WAITING_APPROVAL",
    },
    plan: {
      incident_id: "INC-011",
      approval_threshold_usd: 50000,
      recommended_option_id: "A",
      recommendation_reason: "SUP-002 is the highest-reliability option within acceptable lead time.",
      options: [
        { option_id: "A", total_cost: 93000, max_delivery_days: 7, constraints_satisfied: true },
        { option_id: "B", total_cost: 65000, max_delivery_days: 14, constraints_satisfied: false, rejection_reason: "Lead time exceeds assembly runway" },
      ],
    },
  },
  {
    incident: {
      incident_id: "INC-003",
      severity: "HIGH",
      type: "SUPPLIER_DELAY",
      affected_component: "CMP-003",
      affected_po: "PO-007",
      status: "WAITING_APPROVAL",
    },
    plan: {
      incident_id: "INC-003",
      approval_threshold_usd: 50000,
      recommended_option_id: "A",
      recommendation_reason: "Only option that meets quality and delivery requirements. Exceeds ₹50k threshold.",
      options: [
        { option_id: "A", total_cost: 72000, max_delivery_days: 5, constraints_satisfied: true },
        { option_id: "B", total_cost: 50000, max_delivery_days: 30, constraints_satisfied: false, rejection_reason: "Delivery window 30 days exceeds required 5 days" },
      ],
    },
  },
];

export default function ApprovalsPage() {
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    listIncidents("operational")
      .then(async (incidents) => {
        const waiting = incidents.filter((i) => i.status === "WAITING_APPROVAL");
        const withPlans = await Promise.all(
          waiting.map(async (incident) => {
            try {
              const plan = await getAgentPlan(incident.incident_id);
              return { incident, plan };
            } catch {
              return null;
            }
          })
        );
        const valid = withPlans.filter(Boolean);
        setPending(valid.length > 0 ? valid : FALLBACK_APPROVALS);
      })
      .catch(() => setPending(FALLBACK_APPROVALS))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <div className="loading-shell" style={{ padding: 40, textAlign: "center" }}>
        <span className="loading-orb" />
        <span style={{ marginLeft: 10, fontSize: 14, color: "var(--text-secondary)" }}>Loading pending approvals…</span>
      </div>
    );
  }

  const itemsToRender = pending.length > 0 ? pending : FALLBACK_APPROVALS;

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto" }}>
      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
          Executive Governance & Approvals
        </h1>
        <div style={{ color: "var(--text-muted)", fontSize: 14, marginTop: 4 }}>
          Decisions above the autonomous-execution threshold (₹50,000), awaiting human coordinator authorization.
        </div>
      </div>

      {/* Approvals Cards Feed */}
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {itemsToRender.map(({ incident, plan }) => (
          <ApprovalCard key={incident.incident_id} plan={plan} incident={incident} onDecided={load} />
        ))}
      </div>
    </div>
  );
}