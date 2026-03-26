from __future__ import annotations

import logging

from app.models.entities import GraphEdge, IngestionDocument, PipelineResult
from app.nlp.contradiction import detect_contradiction
from app.nlp.events import classify_event
from app.nlp.geo import geotag_text
from app.nlp.ner import extract_entities
from app.nlp.relation import extract_relations


logger = logging.getLogger(__name__)


class NLPPipeline:
    def __init__(self, graph_client) -> None:
        self.graph_client = graph_client

    def run(self, document: IngestionDocument) -> PipelineResult:
        known_nodes = self.graph_client.list_nodes()
        full_text = f"{document.title}. {document.body}".strip()
        entities = extract_entities(full_text, known_nodes)
        entity_texts = [entity.text for entity in entities]
        relations = extract_relations(full_text, entity_texts)
        contradictions: list[str] = []

        for relation in relations:
            candidate = GraphEdge(
                id=f"candidate-{document.id}-{relation.head}-{relation.tail}-{relation.rel.value}",
                source=relation.head,
                target=relation.tail,
                type=relation.rel,
                confidence=relation.confidence,
                strength=relation.confidence,
                current_strength=relation.confidence,
                source_url=document.source_url,
                source_credibility=0.5,
                created_at=document.published_at,
                updated_at=document.published_at,
                decay_rate=0.2,
                tags=[document.domain.value.lower()],
                properties=relation.properties,
            )
            contradictions.extend(detect_contradiction(self.graph_client.list_edges(), candidate))

        logger.info("NLP processed document %s with %s entities and %s relations", document.id, len(entities), len(relations))
        return PipelineResult(
            document=document,
            entities=entities,
            relations=relations,
            event_type=classify_event(full_text),
            geotags=geotag_text(full_text),
            contradictions=contradictions,
        )
