# Gap Analysis: `supply-chain-resilience-agent` vs. Problem Statement

## Verdict

The submission does not currently satisfy the core requirement of the problem statement. The problem statement is explicit:

> "This is not a chatbot, dashboard, document assistant, or **fixed automation workflow**. The expected solution is an agentic operations controller that can act over multiple steps, recover from uncertainty, and produce a verifiable decision trail."

The current architecture is, structurally, a fixed automation workflow with one LLM classification step embedded in it. That is the exact anti-pattern the problem statement names.

---

## Confirmed directly from `supply_chain_n8n_integration.json`

Opening the actual n8n export removes any ambiguity:

- The `[MAIN AGENT]` section is: one webhook → one code node that builds a single text prompt → **one call** to `lmChatGroq` (LLaMA-3.3-70B) → a parser that extracts one JSON field, `decision`, restricted to exactly four hardcoded values: `APPROVE_AUTONOMOUS`, `NEEDS_HUMAN_APPROVAL`, `DATA_INCONSISTENCY`, `ESCALATE_NO_RESOLUTION`.
- Routing after that point is done by an n8n **Switch node** matching on the literal string value of `decision` — not by the model choosing or invoking anything.
- The prompt itself hands the model a pre-written "anomaly detection checklist" and pre-written "routing rules" (e.g. *"APPROVE_AUTONOMOUS: Recovery cost <= $X AND low risk AND no anomalies"*) to apply. The reasoning boundaries are authored into the prompt template, not discovered by the agent.
- There is no second LLM call for this incident under any branch — no follow-up question, no re-prompt with new data, no tool call emitted by the model.
- A full-text search of all 103 node names for `rfq`, `quote`, `negotiat`, `split`, `replan`, `decompos` returns **zero matches**. There is no RFQ generation, no supplier negotiation, no order-splitting, and no replanning path anywhere in the workflow — only ERP/webhook sync, one scheduled monitor, one LLM classification, and email/audit plumbing.

This confirms the architectural conclusion below is not speculative — it is exactly what the workflow file implements.

## Why this is a fixed workflow, not an agent

| Architecture element | What it actually is |
|---|---|
| n8n graph: `ERP SYNC → MONITOR → SUPPLIER SYNC → MAIN AGENT → APPROVAL` | A static, pre-authored sequence of steps. Every incident goes through the same node graph regardless of what kind of disruption it is. |
| `[MAIN AGENT]` node (Groq LLaMA-3.3-70B) | Fetches pre-assembled context and returns one of two labels: `APPROVE_AUTONOMOUS` or `NEEDS_HUMAN_APPROVAL`. This is a classifier, not a planner. |
| "Golden rule": *"The LLM never performs financial/inventory math itself — it only reasons over context and chooses APPROVE_AUTONOMOUS or NEEDS_HUMAN_APPROVAL"* | This explicitly caps the LLM's role at a single binary decision. All comparison, calculation, and option-generation happens in deterministic Python (`decision_engine/`) *before* the LLM is invoked. |
| `agent/` folder comment: *"Agent state machine (no LLM — reasoning in n8n)"* | Confirms there is no multi-step reasoning loop anywhere in the codebase. The "state machine" just tracks status labels (`INVESTIGATING`, `WAITING_APPROVAL`, `EXECUTING`, `REPLANNING`); it does not itself decompose problems or choose actions. |
| Tool orchestration | Which tools get called, in what order, is determined by the n8n node graph at design time — not by the agent at runtime based on the specific disruption. Section 4.3 of the problem statement requires the *agent* to decide tool use based on current state. |

None of this is disqualifying because n8n was used — it's disqualifying because **the decision loop the problem statement asks for (detect → investigate → decompose → select tools → negotiate → compare → decide → act/escalate → replan) has been replaced by a fixed graph plus one classification call.**

---

## Section-by-section gaps

### 4.2 Dynamic Task Decomposition — **Missing**
The problem statement wants the agent to break a disruption into sub-tasks itself, without being hardcoded for one scenario. Here, the "decomposition" is n8n's node graph — identical for every incident. There is no mechanism for the agent to decide, e.g., "this disruption doesn't need a supplier RFQ, only a schedule check" versus "this one needs three RFQs and a split-order comparison."

### 4.3 Tool Selection — **Missing**
The LLM never chooses which tool to call next. The n8n graph calls tools in a fixed order; the LLM only sees the aggregated result and classifies it.

### 4.4 Supplier Communication — **Weak**
Supplier RFQ handling is a webhook sync (`/supplier-response`), i.e., data ingestion, not negotiation. There's no evidence the agent asks follow-up questions, challenges a vague/contradictory reply, or requests clarification — all explicitly called out in the problem statement (4.4: "Challenge vague or contradictory supplier replies").

### 4.6 Supplier and RFQ Evaluation — **Partially present, but not agent-driven**
Comparison across price/lead time/reliability/quality appears to live in the deterministic `decision_engine/`, which is good practice for the *math*, but the problem statement wants the *agent's reasoning* — not just a lookup table — to justify why a split-order plan was chosen over alternatives, referencing the specific trade-offs (see the Section 17 example output). Currently the LLM only gets asked to approve/escalate a plan someone else already fully computed.

### 4.8 Replanning and Recovery — **Unclear / likely absent**
`REPLANNING` exists as a status label, but nothing in the README indicates what happens when, e.g., a supplier contradicts an earlier promise mid-flight, or a cheaper supplier fails a quality check *after* being selected. A real replanning loop needs the agent to re-enter its reasoning process with updated facts — not just flip a status flag.

### 4.9 Human Escalation — **Reduced to a single threshold check**
Escalation criteria in the problem statement include quality risk, no supplier meeting the deadline, and multiple options with serious trade-offs — not just "cost exceeds `AUTONOMOUS_APPROVAL_LIMIT_USD`." Right now escalation logic appears to be one dollar-amount comparison, which is a business rule, not agentic judgment.

### 4.10 Audit Trail — **Present but likely shallow**
An `/audit` endpoint and log exist, but per the "golden rule," the LLM doesn't do the calculations, so the audit trail is unlikely to contain the rich reasoning trace the problem statement wants (alternatives considered, why they were rejected, confidence in the decision, remaining risk) — see the Section 17 example output for the bar this needs to clear.

---

## Required changes

### 1. Replace the fixed n8n graph as the decision-maker
Keep n8n (or similar) for *infrastructure glue* only — scheduling, webhooks, email delivery, credential management. Move the actual reasoning loop into a real agent runtime that:
- Owns an explicit loop: **observe → decide next tool → act → observe result → decide again**, continuing until the incident is resolved or escalated.
- Uses function/tool calling (Anthropic, OpenAI, or an agent framework such as LangGraph/CrewAI) where the *model itself* selects which tool to call next, not a pre-drawn graph.
- Can vary its own path per incident — a low-severity delay might take 2 tool calls; a multi-supplier disruption might take 15.

### 2. Give the LLM the actual reasoning job, not a label
Stop capping the LLM at `APPROVE_AUTONOMOUS` / `NEEDS_HUMAN_APPROVAL`. Deterministic code should still do arithmetic (correct call), but the LLM should:
- Decide *which* comparisons and calculations are needed for this specific disruption.
- Generate the plan (e.g., "split 600 units from SUP-42, 300 from SUP-37") and the justification, not just bless a plan generated elsewhere.
- Only then have deterministic code validate the arithmetic behind that plan.

### 3. Add genuine dynamic task decomposition
On each new incident, have the agent produce its own task list (in the style of Section 4.2's example decomposition) before acting, and let that list vary by incident type/severity — not a fixed sequence.

### 4. Build real supplier negotiation, not one-shot sync
Simulate suppliers as an interactive counterpart (even a simple LLM-driven supplier persona) so the agent must send a message, receive a reply that may be vague/contradictory, and decide whether to accept it, push back, or escalate. This is required by 4.4 and feeds directly into "detect misleading supplier claims" in the Layer 3 bar (Section 12).

### 5. Implement an actual replanning trigger
Define concrete mid-flight events (a supplier walks back a promise, inventory numbers are corrected, a cheaper vendor fails quality) that interrupt an in-progress plan and re-invoke the agent's reasoning loop with updated facts — not just a status relabel.

### 6. Broaden escalation logic beyond a dollar threshold
Encode the other escalation triggers from 4.9 (no supplier meets the deadline, high quality risk, serious multi-way trade-offs) as conditions the agent itself evaluates, not just a config constant.

### 7. Deepen the audit trail schema
Every incident's audit record should capture, per the Section 4.10 list: data sources checked, supplier messages sent/received, alternatives considered (and why rejected), calculations performed, the decision, the reason, ERP updates made, escalations triggered, and remaining risk — closely mirroring the Section 17 example output. Right now this likely only logs API calls and the final label.

### 8. Update positioning language to match reality (or fix the build first)
The README currently claims things like "constraint-aware recovery planning" and "multi-modal shipment re-routing." Until the above changes land, this framing overstates what the system does — a static pipeline with one classification call isn't "planning." Either build the capability, or don't claim it in submission materials; judges evaluating against this problem statement will look for exactly this gap.

---

## Bottom line

This can likely be salvaged without a full rewrite: the deterministic `decision_engine/`, data model, and simulator sound reusable. The fix is architectural — move from *"n8n pipeline calls an LLM once to approve/escalate"* to *"an agent runtime that owns multi-step reasoning, tool selection, and replanning, with deterministic code as tools it calls."* That shift is what turns this from a fixed workflow with an AI-flavored gate into the "agentic operations controller" the problem statement is asking for.
