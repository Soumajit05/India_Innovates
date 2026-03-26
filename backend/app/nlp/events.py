from __future__ import annotations

from app.models.entities import Domain


def classify_event(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("monsoon", "drought", "climate", "rainfall")):
        return "Climate shock"
    if any(term in lowered for term in ("fed", "inflation", "exchange rate", "market", "price")):
        return "Macro-financial shock"
    if any(term in lowered for term in ("blockade", "conflict", "border", "defense")):
        return "Geostrategic shock"
    if any(term in lowered for term in ("chip", "semiconductor", "it sector", "technology")):
        return "Technology supply shock"
    return "Strategic update"


def infer_domain(text: str) -> Domain:
    event_type = classify_event(text)
    if "Climate" in event_type:
        return Domain.CLIMATE
    if "Macro" in event_type:
        return Domain.ECONOMICS
    if "Technology" in event_type:
        return Domain.TECHNOLOGY
    return Domain.GEOPOLITICS
