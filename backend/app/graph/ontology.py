from __future__ import annotations

from app.models.entities import Domain, EdgeType


EDGE_DESCRIPTIONS: dict[EdgeType, str] = {
    EdgeType.CAUSES: "direct causal effect",
    EdgeType.CORRELATES_WITH: "moves in tandem with",
    EdgeType.THREATENS: "creates strategic or operational risk for",
    EdgeType.ENABLES: "supports or increases capacity for",
    EdgeType.DEGRADES: "reduces resilience or performance of",
    EdgeType.DEPENDS_ON: "has a material dependency on",
    EdgeType.CONTRADICTS: "directly conflicts with",
    EdgeType.SIGNALS: "is an early warning signal for",
    EdgeType.STABILIZES: "reduces volatility or risk in",
    EdgeType.IMPACTS: "has measurable impact on",
}


EDGE_POLARITY: dict[EdgeType, float] = {
    EdgeType.CAUSES: 1.0,
    EdgeType.CORRELATES_WITH: 0.8,
    EdgeType.THREATENS: -1.0,
    EdgeType.ENABLES: 0.7,
    EdgeType.DEGRADES: -0.9,
    EdgeType.DEPENDS_ON: -0.7,
    EdgeType.CONTRADICTS: 0.0,
    EdgeType.SIGNALS: 0.5,
    EdgeType.STABILIZES: 0.6,
    EdgeType.IMPACTS: 0.7,
}


DOMAIN_ORDER: list[Domain] = [
    Domain.GEOPOLITICS,
    Domain.ECONOMICS,
    Domain.DEFENSE,
    Domain.TECHNOLOGY,
    Domain.CLIMATE,
    Domain.SOCIETY,
]
