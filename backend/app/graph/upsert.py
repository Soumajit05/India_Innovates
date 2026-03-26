from __future__ import annotations

import logging
from datetime import datetime, timezone
from hashlib import sha1
from urllib.parse import urlparse

from app.models.entities import Domain, EdgeType, GraphEdge, GraphNode, IngestionDocument, NodeLabel


logger = logging.getLogger(__name__)


CREDIBILITY_REGISTRY: dict[str, float] = {
    "worldbank.org": 0.95,
    "imf.org": 0.95,
    "rbi.org.in": 0.95,
    "reuters.com": 0.80,
    "bbc.com": 0.80,
    "thehindu.com": 0.80,
    "ap.org": 0.80,
    "hindustantimes.com": 0.72,
    "timesofindia.com": 0.72,
    "orfonline.org": 0.70,
    "brookings.edu": 0.70,
    "sipri.org": 0.70,
    "twitter.com": 0.45,
    "x.com": 0.45,
    "DEFAULT": 0.50,
}


def get_source_credibility(url: str) -> float:
    hostname = (urlparse(url).hostname or "").lower()
    if not hostname:
        return CREDIBILITY_REGISTRY["DEFAULT"]
    if hostname in CREDIBILITY_REGISTRY:
        return CREDIBILITY_REGISTRY[hostname]
    for key, value in CREDIBILITY_REGISTRY.items():
        if key == "DEFAULT":
            continue
        if key in hostname or hostname in key:
            return value
    return CREDIBILITY_REGISTRY["DEFAULT"]


class GraphUpsertService:
    def __init__(self, graph_client) -> None:
        self.graph_client = graph_client

    def load_seed_graph(self, nodes: list[GraphNode], edges: list[GraphEdge]) -> None:
        for node in nodes:
            self.graph_client.upsert_node(node)
        for edge in edges:
            edge.source_credibility = get_source_credibility(edge.source_url)
            self.graph_client.upsert_edge(edge)

    def create_claim_node(self, edge: GraphEdge, suffix: str) -> GraphNode:
        source_node = self.graph_client.get_node(edge.source)
        claim_id = sha1(f"{edge.id}:{suffix}".encode("utf-8")).hexdigest()[:12]
        claim_node = GraphNode(
            id=f"claim-{claim_id}",
            label=NodeLabel.CLAIM,
            name=f"Claim: {edge.source}->{edge.target} {edge.type.value}",
            domain=source_node.domain if source_node else Domain.GEOPOLITICS,
            properties={
                "edge_id": edge.id,
                "value": edge.properties.get("metric_value"),
                "source_url": edge.source_url,
                "source_credibility": edge.source_credibility,
            },
            last_updated=datetime.now(timezone.utc),
        )
        self.graph_client.upsert_node(claim_node)
        return claim_node

    @staticmethod
    def _values_conflict(existing_edge: GraphEdge, new_edge: GraphEdge) -> bool:
        old_value = existing_edge.properties.get("metric_value")
        new_value = new_edge.properties.get("metric_value")
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            if old_value == 0:
                return abs(new_value) > 0
            return abs(old_value - new_value) / max(abs(old_value), 1e-9) > 0.15
        if existing_edge.properties.get("metric_name") and new_edge.properties.get("metric_name"):
            if existing_edge.properties.get("metric_name") == new_edge.properties.get("metric_name"):
                return old_value is not None and new_value is not None and old_value != new_value
        old_direction = existing_edge.properties.get("direction")
        new_direction = new_edge.properties.get("direction")
        return bool(old_direction and new_direction and old_direction != new_direction)

    def detect_contradiction(self, new_edge: GraphEdge) -> GraphEdge | None:
        for existing in self.graph_client.list_edges():
            same_relation = existing.source == new_edge.source and existing.target == new_edge.target and existing.type == new_edge.type
            same_property = (
                existing.source == new_edge.source
                and existing.properties.get("metric_name")
                and existing.properties.get("metric_name") == new_edge.properties.get("metric_name")
            )
            if (same_relation or same_property) and self._values_conflict(existing, new_edge):
                return existing
        return None

    def preserve_contradiction(self, existing_edge: GraphEdge, new_edge: GraphEdge) -> GraphEdge:
        existing_claim = self.create_claim_node(existing_edge, "a")
        new_claim = self.create_claim_node(new_edge, "b")
        contradiction_edge = GraphEdge(
            id=f"contradiction-{existing_claim.id}-{new_claim.id}",
            source=existing_claim.id,
            target=new_claim.id,
            type=EdgeType.CONTRADICTS,
            confidence=1.0,
            strength=1.0,
            current_strength=1.0,
            source_url=new_edge.source_url,
            source_credibility=min(existing_edge.source_credibility, new_edge.source_credibility),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            decay_rate=0.0,
            tags=["contradiction"],
            properties={
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "field": new_edge.properties.get("metric_name", "value"),
                "value_a": existing_edge.properties.get("metric_value"),
                "value_b": new_edge.properties.get("metric_value"),
                "source_a_credibility": existing_edge.source_credibility,
                "source_b_credibility": new_edge.source_credibility,
                "edge_type": "CONTRADICTS",
                "color": "#ff4d4f",
            },
        )
        logger.warning(
            "CONTRADICTION DETECTED: %s --%s--> %s",
            existing_edge.source,
            existing_edge.type.value,
            existing_edge.target,
        )
        self.graph_client.upsert_edge(contradiction_edge)
        return contradiction_edge

    def upsert_edge(self, edge: GraphEdge) -> tuple[GraphEdge, bool]:
        edge.source_credibility = get_source_credibility(edge.source_url)
        existing_conflict = self.detect_contradiction(edge)
        if existing_conflict:
            contradiction = self.preserve_contradiction(existing_conflict, edge)
            return contradiction, True
        return self.graph_client.upsert_edge(edge)

    def upsert_indicator(
        self,
        *,
        indicator_id: str,
        indicator_name: str,
        value: float | None,
        unit: str,
        period: str,
        source_url: str,
    ) -> tuple[int, int]:
        created_nodes = 0
        created_edges = 0
        indicator_node = GraphNode(
            id=indicator_id,
            label=NodeLabel.INDICATOR,
            name=indicator_name,
            domain=Domain.ECONOMICS,
            properties={
                "metric_value": value,
                "metric_name": indicator_name,
                "unit": unit,
                "period": period,
                "aliases": [indicator_name],
            },
            last_updated=datetime.now(timezone.utc),
        )
        _, node_created = self.graph_client.upsert_node(indicator_node)
        created_nodes += int(node_created)

        edge = GraphEdge(
            id=f"{indicator_id}-india-correlation",
            source=indicator_id,
            target="india",
            type=EdgeType.CORRELATES_WITH,
            confidence=0.95,
            strength=0.95,
            current_strength=0.95,
            source_url=source_url,
            source_credibility=get_source_credibility(source_url),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            decay_rate=0.05,
            tags=["worldbank", "economics", "india"],
            properties={
                "metric_value": value,
                "metric_name": indicator_name,
                "unit": unit,
                "period": period,
            },
        )
        _, edge_created = self.upsert_edge(edge)
        created_edges += int(edge_created)
        return created_nodes, created_edges

    def upsert_document_event(self, document: IngestionDocument, related_node_ids: list[str]) -> tuple[int, int]:
        created_nodes = 0
        created_edges = 0
        event_node = GraphNode(
            id=document.id,
            label=NodeLabel.EVENT,
            name=document.title,
            domain=document.domain,
            properties={
                "source_url": document.source_url,
                "source_domain": document.source_domain,
                "tags": document.tags,
                **document.metadata,
            },
            last_updated=document.published_at,
        )
        _, created = self.graph_client.upsert_node(event_node)
        created_nodes += int(created)

        for related_id in related_node_ids:
            edge = GraphEdge(
                id=f"{document.id}-{related_id}-signals",
                source=document.id,
                target=related_id,
                type=EdgeType.SIGNALS,
                confidence=0.72,
                strength=0.72,
                current_strength=0.72,
                source_url=document.source_url,
                source_credibility=get_source_credibility(document.source_url),
                created_at=document.published_at,
                updated_at=document.published_at,
                decay_rate=0.35,
                tags=[document.domain.value.lower(), "live-ingestion"],
                properties={
                    "headline": document.title,
                    "metric_name": document.metadata.get("metric_name"),
                    "metric_value": document.metadata.get("metric_value"),
                },
            )
            _, edge_created = self.upsert_edge(edge)
            created_edges += int(edge_created)

        return created_nodes, created_edges
