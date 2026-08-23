# Decision Frameworks

Covers: Decision-Making Under Uncertainty · Cost of Inaction vs. Cost of Action · Multi-Objective Trade-off Management · Quality-Cost-Speed Governance · Decision Authority & Escalation Governance

## 1. Decision-making under uncertainty

Information will be incomplete, stale, or contradictory more often than not — that's the normal operating condition, not a special case. A defensible decision under uncertainty:

- **States its assumptions explicitly.** If inventory data might be stale, say so and note how that changes the risk if it's wrong in the unfavorable direction.
- **Prefers verifiable claims over asserted ones**, and downgrades trust in a source that's already been caught overstating (a supplier who claimed "dispatched" when tracking showed no pickup has earned a lower trust weighting for the rest of the engagement).
- **Sizes the hedge to the stakes.** For a low-impact, reversible decision, act on the best available estimate. For a high-impact, hard-to-reverse one (e.g., committing to a large emergency PO), spend an extra tool call or two closing the biggest uncertainty gap first — but recognize that certainty is not achievable and waiting indefinitely for it is itself a decision (usually the wrong one).
- **Never silently assumes the optimistic case.** If a supplier says "may be delayed 5-7 days," plan around 7, not 5, unless there's a reason to believe otherwise.

## 2. Cost of inaction vs. cost of action

Every "should we intervene" question is a comparison, not a binary judgment about whether the disruption is "bad." Lay it out as:

- **Cost of action**: the price of the emergency response — expedite fees, price premium of an alternate supplier, cost of splitting an order, management time.
- **Cost of inaction**: what happens if nothing changes — production downtime (lost margin per day, not just "the line stops"), missed customer deadlines (penalty clauses, lost goodwill, possible contract loss), and any cascading effect on other orders.

The comparison, not either number alone, drives the call. A cheap intervention that prevents a large downstream loss is an easy yes even if it "feels" like overreacting to a small delay. An expensive intervention against a low-impact, easily-absorbed delay is usually a no, or at least a case for escalation rather than autonomous action, since it's spending real money to solve a problem that might resolve itself.

## 3. Multi-objective trade-off management

Never collapse a decision to a single metric. The recurring axes are:

- Cost vs. speed
- Cost vs. quality/reliability
- Autonomy (act now) vs. approval risk (escalate)
- Short-term recovery vs. long-term supplier dependency risk
- One customer's commitment vs. another's (when resources are genuinely scarce)

Make the trade-off visible rather than silently picking one axis and calling it optimal. A useful pattern when comparing options:

```
Option A (Supplier X, split order): +cost 12%, -lead time 3 days, quality: certified, reliability: high
Option B (Supplier Y, full order):  +cost 4%,  -lead time 1 day,  quality: below threshold — REJECTED
Option C (Wait + reschedule PROD-914): +cost 0%, deadline risk to PROD-882 unresolved
```

Then state which axis you weighted most heavily and why (usually driven by the business-impact analysis and the criticality classification from `risk-and-continuity.md`).

## 4. Quality-cost-speed governance

Some constraints are not tradeable no matter how attractive the alternative looks on cost or speed:

- Certification/compliance requirements for regulated or safety-relevant components.
- Quality thresholds tied to a customer contract.
- Any constraint explicitly flagged as non-negotiable by the business rules available to you.

When the cheapest or fastest option fails one of these, reject it outright and say so plainly in the audit trail — don't rationalize a way around a hard constraint because it would make the numbers look better. If every compliant option is worse on cost/speed than the rejected one, that's exactly the kind of trade-off that belongs in an escalation, not a workaround.

## 5. Decision authority & escalation governance

Decide autonomously when the action is within known limits: cost under the autonomous approval threshold, no quality/compliance constraint violated, deadline achievable, and no unresolved conflict between critical priorities. Escalate when any of the criteria in the main SKILL.md's "Decision authority and escalation" section apply.

**Decision brief template** for escalations:

```
SITUATION: <one or two sentences — what's at risk and by when>
COST OF INACTION: <business consequence if nothing happens, quantified where possible>
OPTIONS CONSIDERED:
  1. <option> — cost / lead time / quality / reliability — <why rejected or why it's the recommendation>
  2. <option> — ...
RECOMMENDATION: <the option you'd choose if authorized>
WHY THIS NEEDS APPROVAL: <specific trigger — over threshold by X, no certified supplier meets deadline, etc.>
TIME SENSITIVITY: <what happens if approval doesn't arrive by when>
```

Keep it tight — a manager reading this should be able to approve, reject, or ask one follow-up question without needing to reconstruct your investigation from scratch.
