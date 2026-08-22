# Supply Chain Disruption Control Agent
Hackers Occupied Pune 2026 (CodeChef) — Team TRACE

Autonomous AI Supply Chain Control Tower: detects disruptions, investigates with tools,
evaluates constrained recovery plans, executes or escalates to a human, and replans when
reality changes.

> **Architecture:** The backend is a pure **CRUD / data API** (FastAPI + MongoDB Atlas).
> All LLM reasoning is handled by a **Groq AI Agent** (LLaMA-3.3-70B) inside the **n8n workflow**.
> No LLM API key is needed in the backend — only in n8n.

---

## Folder Map & Ownership

```
supply-chain-resilience-agent/
├── backend/                     Python 3.10+ · FastAPI · PyMongo · MongoDB Atlas
│   └── app/
│       ├── main.py              App entrypoint, mounts all routers              [Dev 2]
│       ├── config.py            Env/config loading (no LLM keys)                [Dev 2]
│       ├── mongo_database.py    PyMongo Atlas connection                        [Dev 2]
│       ├── models/              MongoDB document shapes                         [Dev 2]
│       ├── schemas/             Pydantic request/response models                [Dev 2, shared]
│       ├── api/
│       │   ├── routes_agent.py         /agent/* — state machine endpoints       [Dev 1+2]
│       │   ├── routes_integrations.py  /integrations/* — n8n-only endpoints     [Dev 2]  ← NEW
│       │   ├── routes_audit.py         /audit/*                                 [Dev 2]
│       │   ├── routes_incidents.py     /incidents/*                             [Dev 2]
│       │   ├── routes_inventory.py     /inventory/*                             [Dev 2]
│       │   ├── routes_suppliers.py     /suppliers/*                             [Dev 2]
│       │   ├── routes_production.py    /production/*                            [Dev 2]
│       │   └── routes_simulator.py     /simulator/*                             [Dev 2]
│       ├── agent/               Agent state machine (no LLM — reasoning in n8n) [Dev 1]
│       ├── simulator/           Disruption injector                             [Dev 2]
│       ├── decision_engine/     Deterministic business logic                    [Dev 3]
│       ├── tools/               Agent-callable tool implementations             [Dev 2+3]
│       └── audit/               Audit log writer/reader                         [Dev 2]
├── frontend/                    React Control Tower UI                          [Dev 4]
│   └── src/
│       ├── api/                 fetch wrappers per backend router
│       └── components/          Overview / Incident Command Center / etc.
├── N8N/
│   ├── supply_chain_n8n_integration.json   Full workflow — import into n8n     ← UPDATED
│   ├── N8N_INTEGRATION.md
│   └── README.md
├── docs/                        Contracts all 4 devs must follow
│   ├── API_CONTRACTS.md
│   ├── TOOL_SCHEMAS.md
│   ├── AGENT_STATE_MACHINE.md
│   ├── CHECKLIST.md
│   └── DEMO_SCRIPT.md
├── docker-compose.yml
└── .gitignore
```

---

## Architecture Overview

```
                        ┌─────────────────────────────────────────┐
                        │              n8n Workflow                │
                        │                                          │
  ERP System ──POST──▶ │ [ERP SYNC] Webhook → Validate → Sync     │
                        │                     ↓                    │
  Schedule (5min) ────▶ │ [MONITOR] Get POs → Evaluate → Breach   │
                        │                     ↓                    │
  Suppliers ──POST────▶ │ [SUPPLIER SYNC] Validate → Sync         │
                        │                     ↓                    │
                        │ 🔴 [MAIN AGENT] Groq LLaMA-3.3-70B      │
                        │    Fetches context from backend          │
                        │    Reasons → APPROVE or NEEDS_HUMAN      │
                        │                     ↓                    │
                        │ 🟣 [APPROVAL] Email → Decision Webhook   │
                        │                     ↓                    │
                        │ All audit → POST /integrations/audit     │
                        └──────────────┬──────────────────────────┘
                                       │ REST (X-API-Key)
                        ┌──────────────▼──────────────────────────┐
                        │   FastAPI Backend (port 8000)            │
                        │   MongoDB Atlas                          │
                        │                                          │
                        │  /integrations/erp/event                 │
                        │  /integrations/purchase-orders/active    │
                        │  /integrations/delivery-breach           │
                        │  /integrations/supplier-response         │
                        │  /integrations/audit          ← n8n only │
                        │                                          │
                        │  /agent/trigger  /agent/approve          │
                        │  /agent/reject   /agent/state/:id        │
                        │  /incidents  /inventory  /audit  etc.    │
                        └──────────────┬──────────────────────────┘
                                       │ REST
                        ┌──────────────▼──────────────────────────┐
                        │   React Frontend (port 5173)             │
                        │   Control Tower UI                       │
                        └─────────────────────────────────────────┘
```

**Golden rule:** The LLM (Groq) never performs financial/inventory math itself — it only
*reasons* over context and chooses APPROVE_AUTONOMOUS or NEEDS_HUMAN_APPROVAL. All numbers
come from deterministic Python tools in `decision_engine/`.

---

## Requirement Classification Key
- **REQUIRED** — mandated by the official PS, non-negotiable.
- **RECOMMENDED** — strongly implied / best practice for scoring.
- **CHOSEN** — our team's own implementation decision.
- **OPTIONAL** — nice-to-have if time remains; cut first under time pressure.

---

## Running Locally

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend |
| Node.js | 18+ | Frontend |
| n8n | Latest | AI agent workflow |
| MongoDB Atlas | — | Database (connection string in `.env`) |

---

### Step 1 — Backend

```bash
cd backend

# Windows (PowerShell)
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS/Linux
python -m venv env
source env/bin/activate
pip install -r requirements.txt

# Configure environment
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux

# Edit .env — set your MongoDB Atlas URI:
# MONGO_URI=mongodb+srv://<user>:<password>@supplychaindb.xpj2vyn.mongodb.net/
# MONGO_DB_NAME=supplychaindb
# BACKEND_API_KEY=changeme-secret-key   ← must match n8n env var

# Start the backend (Python 3.10+ required)
uvicorn app.main:app --reload
# API available at: http://localhost:8000
# Swagger docs at:  http://localhost:8000/docs
```

---

### Step 2 — Frontend

```bash
# In a new terminal
cd frontend
npm install
npm run dev
# UI available at: http://localhost:5173
```

---

### Step 3 — n8n Workflow (AI Agent)

**n8n is the LLM reasoning layer — the Groq AI Agent runs here.**

```bash
# Option A: npx (no install required)
npx n8n

# Option B: global install
npm install -g n8n
n8n start

# n8n UI available at: http://localhost:5678
```

**Import the workflow:**
1. Open `http://localhost:5678`
2. **Workflows → Import from file**
3. Select `N8N/supply_chain_n8n_integration.json`

**Configure credentials in n8n:**

| Credential | How to add | Value |
|-----------|-----------|-------|
| **Groq API** | Credentials → Add → Groq API | Your `GROQ_API_KEY` from [console.groq.com](https://console.groq.com) |
| **SMTP** (optional) | Credentials → Add → SMTP | Your mail server settings for approval emails |

**Configure environment variables in n8n:**

Go to **Settings → Variables** (or set via `.env` for self-hosted n8n):

```
BACKEND_URL                = http://localhost:8000
N8N_BASE_URL               = http://localhost:5678
BACKEND_API_KEY            = changeme-secret-key     ← must match backend .env
AUTONOMOUS_APPROVAL_LIMIT_USD = 50000
APPROVAL_APPROVER_NAME     = procurement_manager
APPROVAL_NOTIFY_EMAIL      = procurement@yourcompany.com
NOTIFY_FROM_EMAIL          = noreply@yourcompany.com
OPS_ALERT_EMAIL            = ops@yourcompany.com
```

**Activate the workflow** — toggle the workflow to **Active**.

---

### Option D — Docker (all-in-one)

```bash
docker compose up --build
# backend:  http://localhost:8000  (docs at /docs)
# frontend: http://localhost:5173
# NOTE: n8n must still be run separately (see Step 3 above)
```

---

## Backend API Reference

All endpoints are documented in Swagger at `http://localhost:8000/docs`.

### n8n → Backend Integration Endpoints (`/integrations/*`)
> These are called exclusively by the n8n workflow, not the frontend.
> All require `X-API-Key` header matching `BACKEND_API_KEY`.

| Method | Path | Called by |
|--------|------|-----------|
| `POST` | `/integrations/erp/event` | ERP Event Sync workflow |
| `GET` | `/integrations/purchase-orders/active` | Delivery Monitor (every 5 min) |
| `POST` | `/integrations/delivery-breach` | Delivery Monitor on breach |
| `POST` | `/integrations/supplier-response` | Supplier Response Sync workflow |
| `POST` | `/integrations/audit` | Every workflow section — persists to MongoDB `audit_logs` |

### Agent State Machine (`/agent/*`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/agent/trigger` | n8n triggers agent; returns incident context for Groq |
| `GET` | `/agent/state/{incident_id}` | Current state (INVESTIGATING / WAITING_APPROVAL / …) |
| `GET` | `/agent/plan/{incident_id}` | Recovery plan for Approval UI |
| `POST` | `/agent/approve` | Mark incident EXECUTING (autonomous or human approval) |
| `POST` | `/agent/reject` | Mark incident REPLANNING |

### Frontend Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/incidents` | All incidents (Overview dashboard) |
| `GET` | `/incidents/{id}` | Single incident |
| `GET` | `/incidents/{id}/activity` | Agent activity feed (audit logs) |
| `GET` | `/inventory` | Inventory levels |
| `GET` | `/suppliers` | Supplier list |
| `GET` | `/production` | Production orders |
| `GET` | `/audit` | Full audit timeline |
| `GET` | `/health` | Liveness check |

---

## n8n Workflow Sections

The workflow is divided into **6 colour-coded sections** (visible as sticky notes after import):

| Label | Colour | Role |
|-------|--------|------|
| `[ERP SYNC]` | 🟦 Blue | Receives ERP purchase order events, syncs to backend, triggers agent on DELAYED status |
| `[MONITOR]` | 🟨 Yellow | Scheduled every 5 min — detects delivery commitment breaches |
| `[SUPPLIER SYNC]` | 🟩 Green | Receives and validates RFQ responses from suppliers |
| `[MAIN AGENT]` | 🔴 Red | **Groq LLaMA-3.3-70B** — the primary LLM reasoning node |
| `[APPROVAL]` | 🟣 Purple | Human approval email flow + decision webhook |
| `[ERROR]` | 🔶 Orange | Global error handler → audit log |

---

## Environment Variables Reference

### `backend/.env`

```env
# MongoDB Atlas (required)
MONGO_URI=mongodb+srv://<user>:<password>@supplychaindb.xpj2vyn.mongodb.net/
MONGO_DB_NAME=supplychaindb

# n8n integration auth
N8N_BASE_URL=http://localhost:5678
BACKEND_API_KEY=changeme-secret-key

# Business rules
AUTONOMOUS_APPROVAL_LIMIT_USD=50000

# CORS (frontend origin)
CORS_ORIGINS=http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

> **Note:** No `LLM_API_KEY`, `LLM_PROVIDER`, or `LLM_MODEL` needed — all LLM calls
> are made inside the n8n Groq AI Agent node.

### `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Team Integration Checkpoints (from team plan, Section 21)
See `docs/CHECKLIST.md` for the full feature list and `docs/DEMO_SCRIPT.md` for the rehearsed
end-to-end demo flow.
