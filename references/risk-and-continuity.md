# Risk & Continuity

Covers: Supply Chain Resilience · Business Continuity & Operational Resilience · Supply Chain Risk Management · Business Impact Analysis · Exception Management & Continuous Monitoring

## 1. Supply chain resilience — design, not just reaction

Resilience is the property of a supply chain that lets it absorb a shock without a proportional hit to the business. When reasoning about a disruption, ask whether the *design* of the current setup caused the impact to be worse than it needed to be — single-sourced components, thin buffers, or suppliers concentrated in one region all convert a small event into a large one. When recommending a recovery plan, prefer options that also reduce this fragility going forward (e.g., qualifying a second supplier) over options that only patch the immediate gap, when the two are close in cost/speed.

## 2. Business continuity — what "critical" actually means

Not all operations deserve the same protection. Before deciding how hard to fight for something, classify it:

- **Critical**: contractual penalty, safety impact, or loss of a strategic customer if it fails. These get first claim on scarce resources and the highest tolerance for emergency cost.
- **Important**: real cost or reputational impact, but the business survives a short delay.
- **Deferrable**: can slip without meaningful consequence.

A continuity plan says, in advance, what the fallback is for each critical operation if normal supply fails — e.g., "if COMP-104 is short, PROD-882 draws down safety stock first, PROD-914 is the one that slips." When no such plan exists, construct this ordering yourself from priority, deadline, and contractual data before allocating anything.

## 3. Supply chain risk management — the ID → assess → prioritize → mitigate cycle

Run every risk (supplier, inventory, logistics, quality, demand) through the same cycle:

1. **Identify**: what could go wrong, from any signal — a vague supplier reply, a stale-looking inventory number, a single-source dependency, a demand spike.
2. **Assess**: likelihood × business impact (use the impact-translation method below). A risk that's likely but low-impact is not the same priority as one that's unlikely but catastrophic.
3. **Prioritize**: rank risks so effort goes to the ones that matter, not the ones that are loudest.
4. **Mitigate**: choose an action sized to the risk — a minor stock gap might just need monitoring; a critical single-source shortage needs an active recovery plan.

Don't treat every alert as equally urgent. The point of this cycle is triage, not blanket escalation.

## 4. Business impact analysis — translate events into consequences

This is the step that turns "PO delayed 5 days" into something a business can act on. Work through:

- **Production impact**: given usable stock, daily consumption, and safety stock, how many days of coverage remain? (`days_of_coverage = (usable_stock - safety_stock) / daily_usage`, floor at 0 — don't count safety stock as available unless a justified decision has been made to consume it.)
- **Deadline impact**: does the shortfall land before or after the production deadline for orders needing this component?
- **Customer/revenue impact**: what orders, contracts, or customer commitments sit behind the affected production? Is there a penalty clause?
- **Downstream impact**: does this cascade into other production lines or components?

Always express the finding in business terms, not just technical ones: not "4.3 days of coverage" alone, but "4.3 days of coverage against a deadline that needs 7, threatening a 700-unit high-priority order due Sept 6." That reframing is what separates an operations controller from a monitoring dashboard.

## 5. Exception management & continuous monitoring

Treat monitoring as a loop, not a one-time check:

- **Detect early**: look past the obvious alert for what it implies downstream (a supplier delay on a component feeding three production orders is three risks, not one).
- **Prioritize**: use the risk cycle above — don't let a noisy but harmless exception consume the same attention as a quiet but severe one.
- **Intervene**: act at the smallest effective scope — don't trigger a full emergency-procurement response for something a minor reschedule would fix.
- **Verify**: after taking an action (a supplier promise, a rescheduled delivery), confirm it actually happened rather than assuming compliance. This closes the loop back into detection for the next cycle.
- **Escalate**: only per the criteria in `decision-frameworks.md` — exception management is about noticing and triaging, not about forwarding every anomaly to a human.

A good operator running this loop develops a sense for which components/suppliers are "always a little late but never actually a problem" versus which ones deserve a lower trust threshold — track that pattern across a session or engagement rather than treating every event as independent.
