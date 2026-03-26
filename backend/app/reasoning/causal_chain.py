from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.graph.confidence import propagate_confidence
from app.models.entities import GraphEdge, GraphNode


logger = logging.getLogger(__name__)


@dataclass
class CausalChainResult:
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    chain_confidence: float
    path: list[str]
    time_to_impact_days: int
    warnings: list[str] = field(default_factory=list)


class CausalChainTracer:
    def __init__(self, graph_client) -> None:
        self.graph_client = graph_client

    def find_strongest_path(self, start_id: str, target_id: str, max_depth: int = 6) -> CausalChainResult | None:
        best_path: tuple[list[str], list[GraphEdge], float, int, list[str]] | None = None

        def dfs(current_id: str, target: str, path_nodes: list[str], path_edges: list[GraphEdge], depth: int) -> None:
            nonlocal best_path
            if depth > max_depth:
                return
            if current_id == target and path_edges:
                confidence = propagate_confidence([edge.current_strength for edge in path_edges])
                time_to_impact = sum(int(edge.properties.get("lag_days", edge.properties.get("time_to_impact_days", 7))) for edge in path_edges)
                warnings: list[str] = []
                if any(edge.is_stale for edge in path_edges):
                    warnings.append("Warning: chain contains stale edges — confidence may be overstated")
                    logger.warning("Stale edge used in causal chain %s -> %s", start_id, target_id)
                if not best_path or confidence > best_path[2]:
                    best_path = (path_nodes[:], path_edges[:], confidence, time_to_impact, warnings)
                return

            for edge in self.graph_client.outgoing_edges(current_id):
                if edge.target in path_nodes:
                    continue
                path_nodes.append(edge.target)
                path_edges.append(edge)
                dfs(edge.target, target, path_nodes, path_edges, depth + 1)
                path_nodes.pop()
                path_edges.pop()

        dfs(start_id, target_id, [start_id], [], 0)
        if not best_path:
            return None

        node_lookup = {node.id: node for node in self.graph_client.list_nodes()}
        nodes = [node_lookup[node_id].model_copy(deep=True) for node_id in best_path[0] if node_id in node_lookup]
        readable_path: list[str] = []
        for index, node in enumerate(nodes):
            readable_path.append(node.name)
            if index < len(best_path[1]):
                readable_path.append(best_path[1][index].type.value)
        return CausalChainResult(
            nodes=nodes,
            edges=[edge.model_copy(deep=True) for edge in best_path[1]],
            chain_confidence=best_path[2],
            path=readable_path,
            time_to_impact_days=best_path[3],
            warnings=best_path[4],
        )
