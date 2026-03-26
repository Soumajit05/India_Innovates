# ARGOS Backend

FastAPI backend for ARGOS, an in-memory strategic intelligence engine with graph reasoning, live ingestion, and Claude-backed synthesis.

## Prerequisites

- Python 3.11+
- pip

## Setup

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
uvicorn app.main:app --reload
```

Fill in `ANTHROPIC_API_KEY` in `.env` before using live Claude synthesis.

## Docker

```bash
docker-compose up --build
```

## Demo API Key

Use `argos-demo-key` in the `X-API-Key` header for all `/api/*` endpoints except `/api/health`.

## Endpoints

1. `GET /api/health`

```bash
curl http://127.0.0.1:8000/api/health
```

2. `POST /api/query`

```bash
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: argos-demo-key" \
  -d "{\"query\":\"How does a Taiwan shock affect India IT?\"}"
```

3. `GET /api/query/stream`

```bash
curl "http://127.0.0.1:8000/api/query/stream?query=How%20does%20monsoon%20risk%20affect%20India%3F" \
  -H "X-API-Key: argos-demo-key"
```

4. `GET /api/dashboard/overview`

```bash
curl http://127.0.0.1:8000/api/dashboard/overview \
  -H "X-API-Key: argos-demo-key"
```

5. `GET /api/graph/explorer`

```bash
curl "http://127.0.0.1:8000/api/graph/explorer?search=India" \
  -H "X-API-Key: argos-demo-key"
```

6. `GET /api/alerts`

```bash
curl http://127.0.0.1:8000/api/alerts \
  -H "X-API-Key: argos-demo-key"
```

7. `POST /api/scenarios/simulate`

```bash
curl -X POST http://127.0.0.1:8000/api/scenarios/simulate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: argos-demo-key" \
  -d "{\"trigger_node\":\"US Fed Funds Rate\",\"change_percent\":50}"
```

8. `POST /api/feedback`

```bash
curl -X POST http://127.0.0.1:8000/api/feedback \
  -H "Content-Type: application/json" \
  -H "X-API-Key: argos-demo-key" \
  -d "{\"query_id\":\"demo\",\"rating\":4,\"cited_node_ids\":[\"india\"],\"flagged_edge_ids\":[\"e1\"]}"
```

## Demo Scenario Queries

- What are India's top 5 strategic vulnerabilities right now?
- How would a Taiwan Strait disruption affect India's IT sector and markets?
- If the Fed hikes again, what is the likely causal path into farmer distress in India?
- What does a weak monsoon imply for food CPI, rural distress, and election risk?
- How does Pakistan instability propagate into border security and India's strategic resilience?

## Notes

- Neo4j remains intentionally in-memory for the hackathon build.
- Twitter connector is optional — system works fully without it.
