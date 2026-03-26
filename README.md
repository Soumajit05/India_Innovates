# ARGOS

ARGOS is an India-first ontology intelligence engine that fuses geopolitical, economic, defense, technology, climate, and societal signals into a causal graph that can be queried in natural language.

This repository is a greenfield implementation based on the five project design documents supplied with the workspace. It includes:

- A FastAPI backend with ontology-aware graph models, confidence propagation, temporal decay, contradiction preservation, scenario simulation, and demo ingestion.
- A Next.js intelligence dashboard with a command-center UI, graph explorer, natural-language query workflow, alerts feed, and scenario simulator.
- A seed dataset centered on India-focused strategic vulnerabilities and demo paths from the blueprint.
- Docker and local dev configuration for running the full stack.

## Monorepo Layout

```text
backend/   FastAPI, reasoning engine, graph store, ingestion scaffolding
frontend/  Next.js 14 dashboard, Sigma.js graph explorer, Tailwind UI
```

## Quick Start

1. Copy `.env.example` to `.env`.
2. Start the backend:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

3. Start the frontend:

   ```powershell
   cd frontend
   & "C:\Program Files\nodejs\npm.cmd" install
   & "C:\Program Files\nodejs\npm.cmd" run dev
   ```

4. Or run everything with Docker:

   ```powershell
   docker compose up --build
   ```

## API Surface

- `GET /api/health`
- `GET /api/dashboard/overview`
- `POST /api/query`
- `POST /api/query/stream`
- `GET /api/graph/explorer`
- `GET /api/graph/subgraph/{node_id}`
- `GET /api/alerts`
- `POST /api/scenarios/simulate`
- `GET /api/scenarios/templates`
- `POST /api/ingest/demo`
