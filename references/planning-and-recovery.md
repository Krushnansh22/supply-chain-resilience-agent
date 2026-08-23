# Planning & Recovery

Covers: Contingency & Scenario Planning · Recovery Strategy & Replanning

## 1. Contingency & scenario planning

Before committing to a single recovery plan, sketch what happens under the ways it could go wrong — this doesn't need to be exhaustive, but the obvious failure modes should be named:

- What if the chosen supplier's delivery slips too?
- What if the alternate supplier's quoted quantity or price changes when confirmed?
- What if demand shifts again before the plan completes?

For a high-stakes decision, having a named fallback ("if Supplier X doesn't confirm within N hours, fall back to splitting with Supplier Y") is stronger than a single-path plan with no contingency — it means the next disruption doesn't require starting the whole loop from scratch. Scale the depth of this to the stakes: a low-impact issue doesn't need a written fallback; a plan protecting a critical, deadline-driven order does.

## 2. Recovery strategy & replanning

Treat every disruption as a dynamic problem, not a one-shot decision. A plan built on the information available at the time it was made is only valid until something material changes. Re-enter the control loop (from SKILL.md) whenever:

- A supplier reply contradicts an earlier promise or a tracking check.
- Inventory data is corrected (especially downward).
- Demand increases or a production priority changes.
- An option you were relying on becomes unavailable (expediting falls through, a supplier rejects the quantity, a cheaper supplier fails quality).
- Time has simply passed and a prior confirmation hasn't materialized (e.g., a quote that was time-limited has now expired, or a promised update hasn't arrived).

When replanning:

1. State clearly what changed and how it invalidates (fully or partially) the prior plan — don't silently swap plans without noting the reason, since that reasoning is exactly what the audit trail exists to capture.
2. Reassess business impact with the new information — the severity may have gone up, down, or sideways.
3. Regenerate options rather than assuming the old option set is still the right one — a supplier that just failed to deliver on a promise may deserve a lower weighting even among the remaining choices.
4. Re-check escalation triggers — a plan that didn't need approval before might now, or vice versa.

This loop can run more than once in a single disruption. That's expected, not a sign of failure — a plan that survives contact with reality unchanged is the exception, not the rule, in this kind of environment. What matters is that each revision is visible and justified in the audit trail, so a human reviewing the full episode can see the reasoning evolve rather than just the final state.
