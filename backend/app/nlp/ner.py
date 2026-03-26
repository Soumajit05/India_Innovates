from __future__ import annotations

import logging
import re
from typing import Iterable

from app.models.entities import ExtractedEntity, GraphNode


logger = logging.getLogger(__name__)


SPACY_ENTITY_LABELS = {"GPE", "ORG", "PERSON", "NORP", "FAC", "LOC", "PRODUCT"}

INDIA_ENTITY_ALIASES: dict[str, str] = {
    "Line of Actual Control": "LOC",
    "LAC": "LOC",
    "Line of Control": "LOC",
    "LoC": "LOC",
    "Arunachal Pradesh": "GPE",
    "Ladakh": "GPE",
    "Aksai Chin": "LOC",
    "Doklam": "LOC",
    "RSS": "ORG",
    "AIADMK": "ORG",
    "DMK": "ORG",
    "AAP": "ORG",
    "ISRO": "ORG",
    "HAL": "ORG",
    "BEL": "ORG",
    "DRDO": "ORG",
    "NASSCOM": "ORG",
    "RBI": "ORG",
    "SEBI": "ORG",
    "NITI Aayog": "ORG",
    "MEA": "ORG",
    "PMO": "ORG",
    "MSP": "CONCEPT",
    "kharif": "CONCEPT",
    "rabi": "CONCEPT",
    "CAD": "CONCEPT",
    "FII": "CONCEPT",
    "FDI": "CONCEPT",
    "Nifty": "ORG",
    "Sensex": "ORG",
    "BSE": "ORG",
    "NSE": "ORG",
    "QUAD": "ORG",
    "SCO": "ORG",
    "BRICS": "ORG",
    "BRI": "CONCEPT",
    "Belt and Road": "CONCEPT",
    "Make in India": "POLICY",
    "Atmanirbhar": "POLICY",
    "PLI": "POLICY",
}

try:
    import spacy

    nlp = spacy.load("en_core_web_sm")
except Exception as exc:  # pragma: no cover - depends on local model install
    nlp = None
    logger.warning("spaCy model en_core_web_sm unavailable, falling back to alias-only NER: %s", exc)


def _deduplicate(entities: Iterable[ExtractedEntity]) -> list[ExtractedEntity]:
    best_by_span: dict[tuple[int, int, str], ExtractedEntity] = {}
    for entity in entities:
        key = (entity.start_char, entity.end_char, entity.text.lower())
        current = best_by_span.get(key)
        if current is None or entity.confidence > current.confidence:
            best_by_span[key] = entity
    return sorted(best_by_span.values(), key=lambda item: (item.start_char, item.end_char))


def _alias_matches(text: str, aliases: dict[str, str], confidence: float) -> list[ExtractedEntity]:
    results: list[ExtractedEntity] = []
    for alias, label in aliases.items():
        pattern = re.compile(rf"(?<!\w){re.escape(alias)}(?!\w)", flags=re.IGNORECASE)
        for match in pattern.finditer(text):
            results.append(
                ExtractedEntity(
                    text=match.group(0),
                    label=label,
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=confidence,
                )
            )
    return results


def _graph_aliases(known_nodes: list[GraphNode]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for node in known_nodes:
        aliases[node.name] = node.label.value
        for alias in node.properties.get("aliases", []):
            aliases[str(alias)] = node.label.value
    return aliases


def extract_entities(text: str, known_nodes: list[GraphNode]) -> list[ExtractedEntity]:
    extracted: list[ExtractedEntity] = []

    if nlp is not None:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ not in SPACY_ENTITY_LABELS:
                continue
            extracted.append(
                ExtractedEntity(
                    text=ent.text,
                    label=ent.label_,
                    start_char=ent.start_char,
                    end_char=ent.end_char,
                    confidence=0.75,
                )
            )

    extracted.extend(_alias_matches(text, _graph_aliases(known_nodes), confidence=0.85))
    extracted.extend(_alias_matches(text, INDIA_ENTITY_ALIASES, confidence=0.85))
    return _deduplicate(extracted)
