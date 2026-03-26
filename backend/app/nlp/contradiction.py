from __future__ import annotations

from app.models.entities import GraphEdge


def detect_contradiction(existing_edges: list[GraphEdge], candidate_edge: GraphEdge) -> list[str]:
    notes: list[str] = []
    for edge in existing_edges:
        same_claim = edge.source == candidate_edge.source and edge.target == candidate_edge.target and edge.type == candidate_edge.type
        if not same_claim:
            continue
        old_value = edge.properties.get("metric_value")
        new_value = candidate_edge.properties.get("metric_value")
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)) and old_value != new_value:
            notes.append(
                f"Conflicting values detected for {edge.source}->{edge.target}: {old_value} vs {new_value}."
            )
    return notes
