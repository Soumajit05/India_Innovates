from __future__ import annotations

import logging
import re
from collections import Counter, deque
from dataclasses import dataclass
from typing import Iterable

from app.graph.decay import compute_edge_strength
from app.models.entities import EdgeType, GraphEdge, GraphNode, GraphPayload


logger = logging.getLogger(__name__)


@dataclass
class GraphSearchResult:
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class InMemoryNeo4jClient:
    """
    Lightweight graph engine that keeps the service boundary Neo4j-like while
    using Python dictionaries for hackathon speed.
    """

    def __init__(self, nodes: Iterable[GraphNode] | None = None, edges: Iterable[GraphEdge] | None = None) -> None:
        self.nodes: dict[str, GraphNode] = {node.id: node.model_copy(deep=True) for node in nodes or []}
        self.edges: dict[str, GraphEdge] = {edge.id: edge.model_copy(deep=True) for edge in edges or []}
        self.refresh()

    @staticmethod
    def _normalize_tokens(text: str) -> list[str]:
        return [token for token in re.findall(r"[A-Za-z0-9]+", text.lower()) if token]

    def _decorate_edge(self, edge: GraphEdge) -> GraphEdge:
        prepared = edge.model_copy(deep=True)
        prepared.current_strength = compute_edge_strength(prepared.confidence, prepared.created_at, prepared.decay_rate)
        prepared.strength = prepared.current_strength
        prepared.is_stale = prepared.current_strength < 0.1
        return prepared

    def refresh(self) -> None:
        counts: Counter[str] = Counter()
        for edge_id, edge in list(self.edges.items()):
            prepared = self._decorate_edge(edge)
            self.edges[edge_id] = prepared
            counts[prepared.source] += 1
            counts[prepared.target] += 1
        for node_id, node in list(self.nodes.items()):
            refreshed = node.model_copy(deep=True)
            refreshed.connections = counts[node_id]
            self.nodes[node_id] = refreshed

    def list_nodes(self) -> list[GraphNode]:
        return sorted((node.model_copy(deep=True) for node in self.nodes.values()), key=lambda item: item.name)

    def list_edges(self) -> list[GraphEdge]:
        self.refresh()
        return sorted((self._decorate_edge(edge) for edge in self.edges.values()), key=lambda item: item.current_strength, reverse=True)

    def get_node(self, node_id: str) -> GraphNode | None:
        node = self.nodes.get(node_id)
        return node.model_copy(deep=True) if node else None

    def get_node_by_name(self, name: str) -> GraphNode | None:
        lowered = name.lower()
        for node in self.nodes.values():
            aliases = [alias.lower() for alias in node.properties.get("aliases", [])]
            if node.name.lower() == lowered or lowered in aliases:
                return node.model_copy(deep=True)
        return None

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        edge = self.edges.get(edge_id)
        return self._decorate_edge(edge) if edge else None

    def find_edges(
        self,
        source: str | None = None,
        target: str | None = None,
        rel_type: EdgeType | None = None,
    ) -> list[GraphEdge]:
        matches = []
        for edge in self.edges.values():
            if source and edge.source != source:
                continue
            if target and edge.target != target:
                continue
            if rel_type and edge.type != rel_type:
                continue
            matches.append(self._decorate_edge(edge))
        matches.sort(key=lambda item: item.current_strength, reverse=True)
        return matches

    def get_node_edges(self, node_id: str) -> list[GraphEdge]:
        return self.outgoing_edges(node_id) + self.incoming_edges(node_id)

    def search_nodes(self, query: str) -> list[GraphNode]:
        query_tokens = set(self._normalize_tokens(query))
        scored: list[tuple[int, GraphNode]] = []
        for node in self.nodes.values():
            aliases = [str(alias) for alias in node.properties.get("aliases", [])]
            searchable = " ".join([node.name, node.label.value, node.domain.value, *aliases])
            searchable_tokens = set(self._normalize_tokens(searchable))
            overlap = len(query_tokens.intersection(searchable_tokens))
            if node.name.lower() in query.lower():
                overlap += 2
            if any(alias.lower() in query.lower() for alias in aliases):
                overlap += 2
            if overlap:
                scored.append((overlap + node.connections, node.model_copy(deep=True)))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [node for _, node in scored[:8]]

    def outgoing_edges(self, node_id: str) -> list[GraphEdge]:
        return sorted(
            (self._decorate_edge(edge) for edge in self.edges.values() if edge.source == node_id),
            key=lambda item: item.current_strength,
            reverse=True,
        )

    def incoming_edges(self, node_id: str) -> list[GraphEdge]:
        return sorted(
            (self._decorate_edge(edge) for edge in self.edges.values() if edge.target == node_id),
            key=lambda item: item.current_strength,
            reverse=True,
        )

    def upsert_node(self, node: GraphNode) -> tuple[GraphNode, bool]:
        existing = self.nodes.get(node.id)
        created = existing is None
        if existing:
            merged = existing.model_copy(deep=True)
            merged.name = node.name
            merged.label = node.label
            merged.domain = node.domain
            merged.last_updated = node.last_updated
            merged.properties.update(node.properties)
            self.nodes[node.id] = merged
        else:
            self.nodes[node.id] = node.model_copy(deep=True)
        self.refresh()
        logger.info("Graph upsert node %s (%s)", node.id, "created" if created else "updated")
        return self.nodes[node.id].model_copy(deep=True), created

    def upsert_edge(self, edge: GraphEdge) -> tuple[GraphEdge, bool]:
        existing = self.edges.get(edge.id)
        created = existing is None
        if existing:
            merged = existing.model_copy(deep=True)
            merged.source = edge.source
            merged.target = edge.target
            merged.type = edge.type
            merged.confidence = edge.confidence
            merged.source_url = edge.source_url
            merged.source_credibility = edge.source_credibility
            merged.updated_at = edge.updated_at
            merged.decay_rate = edge.decay_rate
            merged.tags = edge.tags
            merged.properties.update(edge.properties)
            self.edges[edge.id] = merged
        else:
            self.edges[edge.id] = edge.model_copy(deep=True)
        self.refresh()
        logger.info("Graph upsert edge %s (%s)", edge.id, "created" if created else "updated")
        return self._decorate_edge(self.edges[edge.id]), created

    def lower_edge_confidence(self, edge_id: str, delta: float = 0.1) -> GraphEdge | None:
        edge = self.edges.get(edge_id)
        if not edge:
            return None
        edge.confidence = max(0.1, round(edge.confidence - delta, 3))
        edge.properties["user_flagged"] = True
        self.refresh()
        return self._decorate_edge(edge)

    def boost_node_relevance(self, node_id: str, delta: float = 0.1) -> GraphNode | None:
        node = self.nodes.get(node_id)
        if not node:
            return None
        current = float(node.properties.get("relevance_score", 0.0))
        node.properties["relevance_score"] = min(1.0, round(current + delta, 3))
        return node.model_copy(deep=True)

    def recompute_all_edge_strengths(self) -> int:
        self.refresh()
        return len(self.edges)

    def subgraph(
        self,
        seed_nodes: list[str],
        max_level: int = 3,
        allowed_edge_types: set[EdgeType] | None = None,
        min_strength: float = 0.0,
        limit: int = 200,
    ) -> GraphPayload:
        self.refresh()
        visited_nodes: set[str] = {seed for seed in seed_nodes if seed in self.nodes}
        visited_edges: set[str] = set()
        queue: deque[tuple[str, int]] = deque((seed, 0) for seed in visited_nodes)

        while queue and len(visited_nodes) < limit:
            current_id, depth = queue.popleft()
            if depth >= max_level:
                continue
            neighbors = self.outgoing_edges(current_id) + self.incoming_edges(current_id)
            for edge in neighbors:
                if allowed_edge_types and edge.type not in allowed_edge_types:
                    continue
                if edge.current_strength < min_strength:
                    continue
                visited_edges.add(edge.id)
                other_id = edge.target if edge.source == current_id else edge.source
                if other_id not in visited_nodes and len(visited_nodes) < limit:
                    visited_nodes.add(other_id)
                    queue.append((other_id, depth + 1))

        nodes = [self.nodes[node_id].model_copy(deep=True) for node_id in visited_nodes if node_id in self.nodes]
        edges = [self._decorate_edge(self.edges[edge_id]) for edge_id in visited_edges if edge_id in self.edges]
        nodes.sort(key=lambda node: node.connections, reverse=True)
        edges.sort(key=lambda edge: edge.current_strength, reverse=True)
        return GraphPayload(nodes=nodes[:limit], edges=edges[:limit])
