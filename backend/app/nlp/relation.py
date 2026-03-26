from __future__ import annotations

from app.models.entities import EdgeType, ExtractedRelation


RELATION_KEYWORDS: dict[EdgeType, tuple[str, ...]] = {
    EdgeType.CAUSES: ("cause", "raise", "drives", "pushes", "leads to", "impact"),
    EdgeType.THREATENS: ("threat", "risk", "undermine", "pressure"),
    EdgeType.CORRELATES_WITH: ("correlates", "linked", "tracks"),
    EdgeType.DEPENDS_ON: ("depends on", "reliant on"),
    EdgeType.DEGRADES: ("degrades", "hurts", "weakens", "drops"),
    EdgeType.SIGNALS: ("signals", "warns", "indicates"),
}


def extract_relations(text: str, entities: list[str]) -> list[ExtractedRelation]:
    lowered = text.lower()
    relations: list[ExtractedRelation] = []
    if len(entities) < 2:
        return relations
    for relation_type, keywords in RELATION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            relations.append(
                ExtractedRelation(
                    head=entities[0],
                    rel=relation_type,
                    tail=entities[1],
                    confidence=0.62,
                )
            )
    return relations
