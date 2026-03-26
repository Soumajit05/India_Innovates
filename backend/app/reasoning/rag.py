from __future__ import annotations

import logging

from app.models.entities import EdgeType, GraphNode, GraphPayload
from app.nlp.ner import extract_entities
from app.reasoning.causal_chain import CausalChainTracer


logger = logging.getLogger(__name__)


class GraphRAGService:
    def __init__(self, graph_client) -> None:
        self.graph_client = graph_client
        self.chain_tracer = CausalChainTracer(graph_client)
        self.allowed_edge_types = {
            EdgeType.CAUSES,
            EdgeType.CORRELATES_WITH,
            EdgeType.THREATENS,
            EdgeType.ENABLES,
            EdgeType.DEGRADES,
            EdgeType.DEPENDS_ON,
            EdgeType.SIGNALS,
            EdgeType.STABILIZES,
            EdgeType.IMPACTS,
            EdgeType.CONTRADICTS,
        }

    def match_nodes(self, query: str) -> list[GraphNode]:
        matched = self.graph_client.search_nodes(query)
        if matched:
            return matched
        entities = extract_entities(query, self.graph_client.list_nodes())
        names = {entity.text.lower() for entity in entities}
        results: list[GraphNode] = []
        for node in self.graph_client.list_nodes():
            aliases = {str(alias).lower() for alias in node.properties.get("aliases", [])}
            if node.name.lower() in names or aliases.intersection(names):
                results.append(node)
        return results[:6]

    def retrieve_subgraph(self, query: str, max_hops: int = 3, confidence_threshold: float = 0.25) -> tuple[GraphPayload, list[GraphNode]]:
        matched_nodes = self.match_nodes(query)
        if not matched_nodes:
            matched_nodes = self.graph_client.list_nodes()[:3]
        seed_ids = [node.id for node in matched_nodes[:3]]
        subgraph = self.graph_client.subgraph(
            seed_nodes=seed_ids,
            max_level=max_hops,
            allowed_edge_types=self.allowed_edge_types,
            min_strength=confidence_threshold,
        )
        logger.info("GraphRAG matched %s nodes for query '%s'", len(matched_nodes), query[:80])
        return subgraph, matched_nodes

    def find_chain_for_query(self, query: str, matched_nodes: list[GraphNode]) -> object | None:
        if len(matched_nodes) < 2:
            logger.info("No chain computed for query '%s' because fewer than two nodes matched", query[:80])
            return None
        return self.chain_tracer.find_strongest_path(matched_nodes[0].id, matched_nodes[1].id)
