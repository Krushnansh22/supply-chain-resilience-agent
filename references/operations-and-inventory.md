# Operations & Inventory

Covers: Resource Allocation Under Constraints · Production Prioritization · Inventory Strategy & Buffer Management · Demand-Supply Alignment

## 1. Resource allocation under constraints

When inventory, production capacity, transport capacity, or procurement budget is scarce, allocate deliberately rather than first-come-first-served:

1. Rank the competing demands by business criticality (see continuity classification in `risk-and-continuity.md`).
2. Check hard constraints first — deadlines that can't move, contractual commitments, certification requirements. These aren't "high priority," they're gatekeeping filters.
3. Allocate to the highest-priority demand first, but check whether a partial allocation lets you also cover a second important need — don't assume it's all-or-nothing.
4. Re-check the allocation whenever a new constraint or demand appears (see `planning-and-recovery.md`).

## 2. Production prioritization

When multiple products or orders compete for scarce components, rank them using — in rough order of weight — contractual commitment and penalty exposure, deadline proximity, business/strategic criticality (a flagship customer vs. a minor one), profitability, and the cost of delay for each specific order. A "high priority" label on a production order is a strong signal but not the only input — a high-priority order with a distant deadline may reasonably yield scarce stock to a merely "important" order with a deadline tomorrow, if the numbers support it. State the ranking logic explicitly rather than applying it silently, since this is exactly the kind of call that may need to be defended later.

## 3. Inventory strategy & buffer management

Safety stock exists to absorb *some* disruption without a full-blown response — that's its purpose, and using it for that purpose isn't a failure, it's the buffer doing its job. But treat it as a resource with real limits, not a free pool:

- Before consuming safety stock, confirm the disruption is real and the shortfall is likely to persist — don't burn the buffer reacting to a signal that might self-correct.
- Track how much buffer you're proposing to consume and for how long it leaves the component under-protected against a *second* disruption before replenishment lands.
- Record buffer consumption explicitly in the audit trail as its own decision, with justification — "used X days of safety stock to cover the gap while Supplier Y's order arrives" — not folded silently into "used available inventory."
- If a recovery plan would draw safety stock down to zero or leave a critical component unprotected for an extended window, that's a signal worth surfacing (potentially as part of an escalation) even if the immediate math otherwise works.

## 4. Demand-supply alignment

Not every supply shortfall needs a supply-side fix. Before defaulting to expedited procurement or alternate sourcing, check whether the gap can be closed from the demand or production side instead:

- Can a lower-priority production order be rescheduled to free up the component for a higher-priority one, avoiding new spend entirely?
- Has demand itself shifted (a spike or a cancellation) in a way that changes how urgent the supply gap actually is?
- Is the "shortage" actually a timing mismatch — supply arrives in time for the order's real need date even though it's later than originally planned?

Reconcile demand and supply continuously rather than once at the start of the disruption — a production-priority change, a demand spike, or a schedule shift mid-disruption should trigger a re-check of whether the current recovery plan is still the right one (see `planning-and-recovery.md`).
