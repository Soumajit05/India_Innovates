from __future__ import annotations

import logging
import re


logger = logging.getLogger(__name__)


def evaluate_grounding(synthesis_text: str, cited_nodes: list[str], cited_edges: list[str]) -> dict[str, object]:
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", synthesis_text)
        if sentence.strip()
    ]
    grounded_sentences = 0
    ungrounded_sentences: list[str] = []
    markers = [marker.lower() for marker in [*cited_nodes, *cited_edges] if marker]

    for sentence in sentences:
        lowered = sentence.lower()
        if any(marker in lowered for marker in markers):
            grounded_sentences += 1
        else:
            ungrounded_sentences.append(sentence)

    total_sentences = len(sentences)
    grounding_rate = round(grounded_sentences / total_sentences, 3) if total_sentences else 0.0
    if total_sentences and grounding_rate < 0.8:
        logger.warning("Grounding rate below threshold: %.2f", grounding_rate)
    return {
        "total_sentences": total_sentences,
        "grounded_sentences": grounded_sentences,
        "grounding_rate": grounding_rate,
        "ungrounded_sentences": ungrounded_sentences,
    }
