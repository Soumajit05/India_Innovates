from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import create_app


API_KEY = "argos-demo-key"
client = TestClient(create_app(testing=True))


def _headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY}


def test_health_returns_node_count():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["node_count"] >= 38


def test_query_returns_citations():
    response = client.post(
        "/api/query",
        json={"query": "What are India's top 5 strategic vulnerabilities right now?"},
        headers=_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["citations"]


def test_query_with_no_match_graceful():
    response = client.post(
        "/api/query",
        json={"query": "zxqv nonsense orbital mango equilibrium"},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["subgraph"]["nodes"]


def test_scenario_returns_impacts():
    response = client.post(
        "/api/scenarios/simulate",
        json={"trigger_node": "US Fed Funds Rate", "change_percent": 50, "depth": 3},
        headers=_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["impacts"]
    assert "magnitude" in payload["impacts"][0]
    assert "confidence" in payload["impacts"][0]


def test_alerts_returns_list():
    response = client.get("/api/alerts", headers=_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_graph_subgraph_has_edges():
    response = client.get("/api/graph/subgraph/India", headers=_headers())
    assert response.status_code == 200
    assert response.json()["graph"]["edges"]


def test_stream_endpoint_sends_json_lines():
    response = client.get(
        "/api/query/stream",
        params={"query": "How does Taiwan affect India IT?"},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    lines = [line for line in response.text.splitlines() if line.strip()]
    assert lines
    for line in lines:
        json.loads(line)


def test_auth_rejects_missing_key():
    response = client.post("/api/query", json={"query": "test"})
    assert response.status_code == 401
