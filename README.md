# Supply Chain Disruption Control Agent
Hackers Occupied Pune 2026 (CodeChef) — Team TRACE

Autonomous AI Supply Chain Control Tower: detects disruptions, investigates with tools,
evaluates constrained recovery plans, executes or escalates to a human, and replans when
reality changes.

> This repo is a **scaffold**. Every file contains placeholder logic and `# TODO` markers.
> Read `docs/` before writing code — it is the single source of truth for contracts between
> the 4 developer workstreams so nobody blocks anybody else.

## Folder Map & Ownership

```
supply-chain-agent/
├── backend/                     Python + FastAPI + SQLite (simulated ERP)
│   └── app/
│       ├── main.py              App entrypoint, mounts all routers          [Dev 2]
│       ├── config.py            Env/config loading                          [Dev 2]
│       ├── database.py          SQLAlchemy engine/session                   [Dev 2]
│       ├── models/              SQLAlchemy ORM tables (DB schema)           [Dev 2]
│       ├── schemas/              Pydantic request/response models          [Dev 2, shared]
│       ├── api/                 REST endpoints (routers)                    [Dev 2]
│       ├── simulator/           Supplier simulator + disruption injector    [Dev 2]
│       ├── decision_engine/     Deterministic business logic                [Dev 3]
│       ├── tools/               Agent-callable tool implementations         [Dev 2 + Dev 3]
│       ├── agent/               LLM agent loop, tool-calling, replanning    [Dev 1]
│       └── audit/               Audit log writer/reader                     [Dev 2]
├── frontend/                    React Control Tower UI                      [Dev 4]
│   └── src/
│       ├── api/                 fetch wrappers per backend router
│       └── components/          Overview / Incident Command Center / etc.
├── docs/                        Contracts all 4 devs must follow
│   ├── DB_SCHEMA.md
│   ├── API_CONTRACTS.md
│   ├── TOOL_SCHEMAS.md
│   ├── AGENT_STATE_MACHINE.md
│   ├── CHECKLIST.md             <-- feature checklist, use this to track progress
│   └── DEMO_SCRIPT.md
├── docker-compose.yml
└── .gitignore
```

## Data Flow (who hands what to whom)

```
Disruption Simulator (Dev2)  --injects-->  incidents table (DB)
        |
        v
Agent Loop (Dev1)  --calls-->  Tools (Dev2 backend I/O + Dev3 business rules)
        |                              |
        |                              v
        |                     Decision Engine (Dev3): inventory calc, risk,
        |                     supplier scoring, constraint checks, recovery plan
        v
Agent decides: EXECUTE  or  ESCALATE (>$50,000 impact per official PS)
        |
        v
ERP update (Dev2, via update_erp tool)  +  Audit Log (Dev2/Dev3, every tool call & decision)
        |
        v
React Control Tower (Dev4)  <--REST-->  FastAPI (Dev2)
   - polls /incidents, /agent/activity, /audit for live view
   - posts /agent/approve or /agent/reject for human-in-the-loop
```

**Golden rule (from team design doc, Section 4):** the LLM never performs financial/inventory
math itself. It only *chooses tools* and *narrates* results returned by deterministic Python
code in `decision_engine/`. Every number shown to a judge must be traceable to a tool result,
not to model text.

## Requirement Classification Key (used throughout docs/)
- **REQUIRED** — mandated by the official PS (`Assigned_Team_Problem.txt`), non-negotiable.
- **RECOMMENDED** — not explicit in the PS but strongly implied / best practice for scoring.
- **CHOSEN** — our team's own implementation decision (tech stack, DB shape, UI, etc.).
- **OPTIONAL** — nice-to-have if time remains; cut first under time pressure.

## Running locally

### Option A — Docker (recommended for integration checkpoints)
```bash
docker compose up --build
# backend:  http://localhost:8000   (docs at /docs)
# frontend: http://localhost:5173
```

### Option B — Native (recommended for fast individual iteration)
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your LLM_API_KEY
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

## LLM Provider
Default wiring in `backend/app/agent/llm_client.py` targets the **Anthropic Messages API**
(tool-use / function-calling) since that best matches this scaffold's tool-schema format, but
it is written behind a thin interface so swapping to OpenAI/Gemini only touches that one file.
Set `LLM_PROVIDER` in `.env` to switch.

## Team Integration Checkpoints (from team plan, Section 21)
See `docs/CHECKLIST.md` for the full feature list and `docs/DEMO_SCRIPT.md` for the rehearsed
end-to-end demo flow. Stick to the 18-hour timeline in that file — do not add scope after the
Hour 16 demo freeze.
