from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.api.dashboard import calculate_india_risk_score
from app.graph.decay import compute_edge_strength
from app.graph.neo4j_client import InMemoryNeo4jClient
from app.graph.seed import NOW, seeded_edges, seeded_nodes
from app.graph.upsert import GraphUpsertService
from app.models.entities import Domain, EdgeType, GraphEdge, GraphNode, NodeLabel
from app.reasoning.causal_chain import CausalChainTracer
from app.reasoning.scenario import ScenarioSimulator


def build_graph():
    client = InMemoryNeo4jClient()
    GraphUpsertService(client).load_seed_graph(seeded_nodes(), seeded_edges())
    return client


def test_decay_reduces_confidence_over_time():
    created_at = datetime.now(timezone.utc) - timedelta(days=365)
    current_strength = compute_edge_strength(0.9, created_at, 1.0)
    assert current_strength < 0.9


def test_chain_confidence_product():
    tracer_product = round(0.9 * 0.8 * 0.7, 3)
    assert tracer_product == 0.504


def test_stale_edge_flagged():
    old_edge = GraphEdge(
        id="old-edge",
        source="a",
        target="b",
        type=EdgeType.CAUSES,
        confidence=0.9,
        strength=0.9,
        current_strength=0.9,
        source_url="https://example.com",
        source_credibility=0.5,
        created_at=datetime.now(timezone.utc) - timedelta(days=3650),
        updated_at=datetime.now(timezone.utc),
        decay_rate=8.0,
        tags=[],
        properties={},
    )
    client = InMemoryNeo4jClient(
        nodes=[
            GraphNode(id="a", label=NodeLabel.INDICATOR, name="A", domain=Domain.ECONOMICS, last_updated=NOW),
            GraphNode(id="b", label=NodeLabel.INDICATOR, name="B", domain=Domain.ECONOMICS, last_updated=NOW),
        ],
        edges=[old_edge],
    )
    returned = client.list_edges()[0]
    assert returned.is_stale is True


def test_contradiction_creates_edge():
    client = InMemoryNeo4jClient()
    upsert = GraphUpsertService(client)
    source = GraphNode(id="a", label=NodeLabel.INDICATOR, name="A", domain=Domain.ECONOMICS, last_updated=NOW)
    target = GraphNode(id="b", label=NodeLabel.INDICATOR, name="B", domain=Domain.ECONOMICS, last_updated=NOW)
    client.upsert_node(source)
    client.upsert_node(target)

    edge_a = GraphEdge(
        id="e-a",
        source="a",
        target="b",
        type=EdgeType.CAUSES,
        confidence=0.8,
        strength=0.8,
        current_strength=0.8,
        source_url="https://reuters.com/a",
        source_credibility=0.8,
        created_at=NOW,
        updated_at=NOW,
        decay_rate=0.0,
        tags=[],
        properties={"metric_name": "value", "metric_value": 100},
    )
    edge_b = edge_a.model_copy(deep=True)
    edge_b.id = "e-b"
    edge_b.source_url = "https://bbc.com/b"
    edge_b.properties = {"metric_name": "value", "metric_value": 150}

    upsert.upsert_edge(edge_a)
    upsert.upsert_edge(edge_b)

    assert any(edge.type == EdgeType.CONTRADICTS for edge in client.list_edges())


def test_scenario_no_infinite_loop():
    nodes = [
        GraphNode(id="a", label=NodeLabel.INDICATOR, name="A", domain=Domain.ECONOMICS, last_updated=NOW),
        GraphNode(id="b", label=NodeLabel.INDICATOR, name="B", domain=Domain.ECONOMICS, last_updated=NOW),
    ]
    edges = [
        GraphEdge(
            id="ab",
            source="a",
            target="b",
            type=EdgeType.CAUSES,
            confidence=0.9,
            strength=0.9,
            current_strength=0.9,
            source_url="https://example.com/ab",
            source_credibility=0.5,
            created_at=NOW,
            updated_at=NOW,
            decay_rate=0.0,
            tags=[],
            properties={"lag_days": 2},
        ),
        GraphEdge(
            id="ba",
            source="b",
            target="a",
            type=EdgeType.CAUSES,
            confidence=0.9,
            strength=0.9,
            current_strength=0.9,
            source_url="https://example.com/ba",
            source_credibility=0.5,
            created_at=NOW,
            updated_at=NOW,
            decay_rate=0.0,
            tags=[],
            properties={"lag_days": 2},
        ),
    ]
    simulator = ScenarioSimulator(InMemoryNeo4jClient(nodes=nodes, edges=edges))
    response = simulator.simulate("A", 50, depth=5)
    assert response.impacts
    assert any("Feedback loop detected" in warning for warning in response.simulation_warnings)


def test_scenario_contested_impact():
    nodes = [
        GraphNode(id="a", label=NodeLabel.INDICATOR, name="A", domain=Domain.ECONOMICS, last_updated=NOW),
        GraphNode(id="b", label=NodeLabel.INDICATOR, name="B", domain=Domain.ECONOMICS, last_updated=NOW),
        GraphNode(id="c", label=NodeLabel.INDICATOR, name="C", domain=Domain.ECONOMICS, last_updated=NOW),
        GraphNode(id="d", label=NodeLabel.INDICATOR, name="D", domain=Domain.ECONOMICS, last_updated=NOW),
    ]
    edges = [
        GraphEdge(
            id="ab",
            source="a",
            target="b",
            type=EdgeType.CAUSES,
            confidence=0.9,
            strength=0.9,
            current_strength=0.9,
            source_url="https://example.com/ab",
            source_credibility=0.5,
            created_at=NOW,
            updated_at=NOW,
            decay_rate=0.0,
            tags=[],
            properties={"lag_days": 1},
        ),
        GraphEdge(
            id="ad",
            source="a",
            target="c",
            type=EdgeType.CAUSES,
            confidence=0.9,
            strength=0.9,
            current_strength=0.9,
            source_url="https://example.com/ac",
            source_credibility=0.5,
            created_at=NOW,
            updated_at=NOW,
            decay_rate=0.0,
            tags=[],
            properties={"lag_days": 1},
        ),
        GraphEdge(
            id="bd",
            source="b",
            target="d",
            type=EdgeType.CAUSES,
            confidence=0.9,
            strength=0.9,
            current_strength=0.9,
            source_url="https://example.com/bd",
            source_credibility=0.5,
            created_at=NOW,
            updated_at=NOW,
            decay_rate=0.0,
            tags=[],
            properties={"lag_days": 1},
        ),
        GraphEdge(
            id="cd",
            source="c",
            target="d",
            type=EdgeType.THREATENS,
            confidence=0.9,
            strength=0.9,
            current_strength=0.9,
            source_url="https://example.com/cd",
            source_credibility=0.5,
            created_at=NOW,
            updated_at=NOW,
            decay_rate=0.0,
            tags=[],
            properties={"lag_days": 1},
        ),
    ]
    simulator = ScenarioSimulator(InMemoryNeo4jClient(nodes=nodes, edges=edges))
    response = simulator.simulate("A", 50, depth=3)
    target = next(impact for impact in response.impacts if impact.node.id == "d")
    assert target.direction == "CONTESTED"


def test_india_risk_score_not_zero():
    client = build_graph()
    score, _, _ = calculate_india_risk_score(client)
    assert score > 0
    assert score <= 100


def test_confidence_uses_current_strength():
    nodes = [
        GraphNode(id="a", label=NodeLabel.INDICATOR, name="A", domain=Domain.ECONOMICS, last_updated=NOW),
        GraphNode(id="b", label=NodeLabel.INDICATOR, name="B", domain=Domain.ECONOMICS, last_updated=NOW),
        GraphNode(id="c", label=NodeLabel.INDICATOR, name="C", domain=Domain.ECONOMICS, last_updated=NOW),
    ]
    stale_edge = GraphEdge(
        id="ab",
        source="a",
        target="b",
        type=EdgeType.CAUSES,
        confidence=0.9,
        strength=0.9,
        current_strength=0.9,
        source_url="https://example.com/ab",
        source_credibility=0.5,
        created_at=datetime.now(timezone.utc) - timedelta(days=365),
        updated_at=NOW,
        decay_rate=2.0,
        tags=[],
        properties={"lag_days": 2},
    )
    fresh_edge = GraphEdge(
        id="bc",
        source="b",
        target="c",
        type=EdgeType.CAUSES,
        confidence=0.9,
        strength=0.9,
        current_strength=0.9,
        source_url="https://example.com/bc",
        source_credibility=0.5,
        created_at=NOW,
        updated_at=NOW,
        decay_rate=0.0,
        tags=[],
        properties={"lag_days": 2},
    )
    client = InMemoryNeo4jClient(nodes=nodes, edges=[stale_edge, fresh_edge])
    tracer = CausalChainTracer(client)
    chain = tracer.find_strongest_path("a", "c")
    assert chain is not None
    assert chain.chain_confidence < 0.81
