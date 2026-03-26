from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.entities import Domain, EdgeType, GraphEdge, GraphNode, NodeLabel


NOW = datetime(2026, 3, 26, 12, 0, tzinfo=timezone.utc)


def _node(
    node_id: str,
    name: str,
    domain: Domain,
    label: NodeLabel,
    aliases: list[str] | None = None,
    **properties,
) -> GraphNode:
    payload = dict(properties)
    payload["aliases"] = aliases or []
    return GraphNode(
        id=node_id,
        label=label,
        name=name,
        domain=domain,
        properties=payload,
        last_updated=NOW,
    )


def _edge(
    edge_id: str,
    source: str,
    target: str,
    rel_type: EdgeType,
    confidence: float,
    source_url: str,
    decay_rate: float,
    created_days_ago: int,
    tags: list[str],
    **properties,
) -> GraphEdge:
    created_at = NOW - timedelta(days=created_days_ago)
    if "time_to_impact_days" in properties and "lag_days" not in properties:
        properties["lag_days"] = properties["time_to_impact_days"]
    if rel_type == EdgeType.DEPENDS_ON and "dependency_pct" not in properties:
        properties["dependency_pct"] = round(float(properties.get("severity", confidence)) * 100, 1)
    return GraphEdge(
        id=edge_id,
        source=source,
        target=target,
        type=rel_type,
        confidence=confidence,
        strength=confidence,
        current_strength=confidence,
        source_url=source_url,
        source_credibility=0.0,
        created_at=created_at,
        updated_at=NOW,
        decay_rate=decay_rate,
        tags=tags,
        properties=properties,
    )


def seeded_nodes() -> list[GraphNode]:
    return [
        _node("india", "India", Domain.GEOPOLITICS, NodeLabel.COUNTRY, ["Indian economy", "Indian state"], region="South Asia"),
        _node("fed-rate", "US Fed Funds Rate", Domain.ECONOMICS, NodeLabel.INDICATOR, ["US Fed", "Fed rates", "Fed rate hike"]),
        _node("usd-inr", "USD/INR Exchange Rate", Domain.ECONOMICS, NodeLabel.INDICATOR, ["rupee exchange rate", "INR pressure"]),
        _node("brent", "Brent Crude", Domain.ECONOMICS, NodeLabel.INDICATOR, ["oil price", "crude price"]),
        _node("fertilizer-imports", "India Fertilizer Import Cost", Domain.ECONOMICS, NodeLabel.INDICATOR, ["fertilizer cost", "fertilizer imports"]),
        _node("kharif-cost", "Kharif Crop Production Cost", Domain.SOCIETY, NodeLabel.INDICATOR, ["farmer distress", "crop input cost"]),
        _node("msp-politics", "MSP Politics", Domain.SOCIETY, NodeLabel.POLICY, ["support prices", "MSP"]),
        _node("farmer-protests", "Farmer Protest Probability", Domain.SOCIETY, NodeLabel.RISK, ["Indian farmers", "farmer distress"]),
        _node("taiwan-conflict", "Taiwan Strait Conflict", Domain.GEOPOLITICS, NodeLabel.EVENT, ["Taiwan blockade", "China blockades Taiwan"]),
        _node("tsmc", "TSMC Production", Domain.TECHNOLOGY, NodeLabel.ORGANIZATION, ["TSMC", "Taiwan chips"]),
        _node("chip-supply", "Global Semiconductor Supply", Domain.TECHNOLOGY, NodeLabel.INDICATOR, ["chip supply", "semiconductor supply chain"]),
        _node("india-hardware", "India IT Hardware Costs", Domain.TECHNOLOGY, NodeLabel.INDICATOR, ["IT hardware cost", "hardware costs"]),
        _node("india-it", "India IT Sector Growth", Domain.TECHNOLOGY, NodeLabel.SECTOR, ["India's IT sector", "Indian IT sector"]),
        _node("nifty-it", "Nifty IT Index", Domain.ECONOMICS, NodeLabel.INDICATOR, ["IT index", "tech stocks"]),
        _node("fii-outflow", "FII Outflow India Tech", Domain.ECONOMICS, NodeLabel.RISK, ["foreign outflow", "FII outflow"]),
        _node("india-oil-risk", "India Oil Import Dependency", Domain.ECONOMICS, NodeLabel.RISK, ["oil dependency"]),
        _node("semiconductor-imports", "India Semiconductor Import Dependency", Domain.TECHNOLOGY, NodeLabel.RISK, ["chip imports", "semiconductor imports"]),
        _node("water-stress", "India Water Treaty Exposure", Domain.CLIMATE, NodeLabel.RISK, ["water treaties", "water risk"]),
        _node("rare-earths", "Rare Earth Import Exposure", Domain.TECHNOLOGY, NodeLabel.RISK, ["rare earth imports"]),
        _node("pakistan-stability", "Pakistan Stability Index", Domain.GEOPOLITICS, NodeLabel.INDICATOR, ["Pakistan instability", "Pakistan"]),
        _node("border-risk", "India Border Security Risk", Domain.DEFENSE, NodeLabel.RISK, ["border security", "border instability"]),
        _node("lac", "LAC Stability", Domain.DEFENSE, NodeLabel.RISK, ["Line of Actual Control", "LAC"]),
        _node("trade-corridor", "India-Pak Trade Corridor", Domain.ECONOMICS, NodeLabel.SECTOR, ["trade impact"]),
        _node("monsoon", "IMD Monsoon Forecast", Domain.CLIMATE, NodeLabel.INDICATOR, ["below-normal monsoon", "monsoon 2025"]),
        _node("kharif-output", "Kharif Output", Domain.CLIMATE, NodeLabel.INDICATOR, ["crop output"]),
        _node("food-cpi", "Food CPI", Domain.ECONOMICS, NodeLabel.INDICATOR, ["food inflation", "inflation"]),
        _node("rural-distress", "Rural Distress Index", Domain.SOCIETY, NodeLabel.RISK, ["rural distress"]),
        _node("party-support", "Ruling Party Support", Domain.SOCIETY, NodeLabel.INDICATOR, ["electoral support"]),
        _node("election-risk", "State Election Risk", Domain.SOCIETY, NodeLabel.RISK, ["electoral instability", "election risk"]),
        _node("india-strategy", "India Strategic Resilience", Domain.GEOPOLITICS, NodeLabel.INDICATOR, ["strategic vulnerabilities"]),
        _node("maharashtra", "Maharashtra", Domain.SOCIETY, NodeLabel.REGION, ["MH"], state_risk=78.0),
        _node("madhya-pradesh", "Madhya Pradesh", Domain.SOCIETY, NodeLabel.REGION, ["MP"], state_risk=74.0),
        _node("rajasthan", "Rajasthan", Domain.SOCIETY, NodeLabel.REGION, ["RJ"], state_risk=69.0),
        _node("uttar-pradesh", "Uttar Pradesh", Domain.SOCIETY, NodeLabel.REGION, ["UP"], state_risk=81.0),
        _node("bihar", "Bihar", Domain.SOCIETY, NodeLabel.REGION, ["BR"], state_risk=77.0),
        _node("oil-imports", "OPEC Supply", Domain.GEOPOLITICS, NodeLabel.ORGANIZATION, ["OPEC"]),
        _node("rbi-policy", "RBI Policy Response", Domain.ECONOMICS, NodeLabel.POLICY, ["RBI response"]),
        _node("global-drought", "Regional Drought Risk", Domain.CLIMATE, NodeLabel.RISK, ["drought risk"]),
    ]


def seeded_edges() -> list[GraphEdge]:
    return [
        _edge("e1", "india", "india-oil-risk", EdgeType.DEPENDS_ON, 0.92, "https://www.worldbank.org", 0.08, 7, ["economics", "india"], severity=0.84),
        _edge("e2", "india", "semiconductor-imports", EdgeType.DEPENDS_ON, 0.89, "https://www.nasscom.in", 0.08, 12, ["technology", "india"], severity=0.82),
        _edge("e3", "india", "water-stress", EdgeType.THREATENS, 0.81, "https://www.imd.gov.in", 0.15, 14, ["climate", "india"], severity=0.77),
        _edge("e4", "india", "rare-earths", EdgeType.DEPENDS_ON, 0.74, "https://www.reuters.com", 0.18, 18, ["technology", "india"], severity=0.71),
        _edge("e5", "india", "lac", EdgeType.THREATENS, 0.69, "https://www.mea.gov.in", 0.22, 9, ["defense", "india"], severity=0.7),
        _edge("e6", "fed-rate", "usd-inr", EdgeType.CAUSES, 0.87, "https://www.imf.org", 0.12, 8, ["economics"], time_to_impact_days=4),
        _edge("e7", "usd-inr", "brent", EdgeType.CORRELATES_WITH, 0.81, "https://www.worldbank.org", 0.12, 8, ["economics"], time_to_impact_days=3),
        _edge("e8", "brent", "fertilizer-imports", EdgeType.CAUSES, 0.84, "https://www.rbi.org.in", 0.11, 6, ["economics", "india"], time_to_impact_days=10),
        _edge("e9", "fertilizer-imports", "kharif-cost", EdgeType.CAUSES, 0.78, "https://www.mospi.gov.in", 0.13, 6, ["society", "india"], time_to_impact_days=14),
        _edge("e10", "kharif-cost", "msp-politics", EdgeType.CAUSES, 0.76, "https://www.livemint.com", 0.18, 6, ["society"], time_to_impact_days=21),
        _edge("e11", "msp-politics", "farmer-protests", EdgeType.SIGNALS, 0.73, "https://www.thehindu.com", 0.2, 5, ["society"], time_to_impact_days=28),
        _edge("e12", "taiwan-conflict", "tsmc", EdgeType.DEGRADES, 0.88, "https://www.reuters.com", 0.15, 3, ["geopolitics", "technology"], time_to_impact_days=2),
        _edge("e13", "tsmc", "chip-supply", EdgeType.CAUSES, 0.84, "https://www.semiconductors.org", 0.12, 3, ["technology"], time_to_impact_days=4),
        _edge("e14", "chip-supply", "india-hardware", EdgeType.CAUSES, 0.79, "https://www.nasscom.in", 0.1, 3, ["technology", "india"], time_to_impact_days=18),
        _edge("e15", "india-hardware", "india-it", EdgeType.DEGRADES, 0.74, "https://www.reuters.com", 0.16, 3, ["technology", "india"], time_to_impact_days=28),
        _edge("e16", "india-it", "nifty-it", EdgeType.CORRELATES_WITH, 0.71, "https://www.finance.yahoo.com", 0.2, 3, ["economics", "technology"], time_to_impact_days=14),
        _edge("e17", "nifty-it", "fii-outflow", EdgeType.SIGNALS, 0.65, "https://www.bloomberg.com", 0.2, 3, ["economics"], time_to_impact_days=7),
        _edge("e18", "fii-outflow", "usd-inr", EdgeType.CAUSES, 0.62, "https://www.imf.org", 0.18, 3, ["economics"], time_to_impact_days=6),
        _edge("e19", "pakistan-stability", "border-risk", EdgeType.THREATENS, 0.79, "https://acleddata.com", 0.19, 4, ["defense", "geopolitics"], time_to_impact_days=9),
        _edge("e20", "border-risk", "trade-corridor", EdgeType.DEGRADES, 0.67, "https://www.worldbank.org", 0.2, 4, ["economics", "defense"], time_to_impact_days=15),
        _edge("e21", "border-risk", "lac", EdgeType.CORRELATES_WITH, 0.58, "https://www.mea.gov.in", 0.24, 4, ["defense"], time_to_impact_days=12),
        _edge("e22", "monsoon", "kharif-output", EdgeType.CAUSES, 0.82, "https://www.imd.gov.in", 0.1, 2, ["climate"], time_to_impact_days=12, direction="decrease"),
        _edge("e23", "kharif-output", "food-cpi", EdgeType.CAUSES, 0.79, "https://www.rbi.org.in", 0.13, 2, ["economics", "climate"], time_to_impact_days=20),
        _edge("e24", "food-cpi", "rural-distress", EdgeType.CAUSES, 0.76, "https://www.worldbank.org", 0.15, 2, ["society", "economics"], time_to_impact_days=25),
        _edge("e25", "rural-distress", "party-support", EdgeType.DEGRADES, 0.72, "https://www.lokniti.org", 0.18, 2, ["society"], time_to_impact_days=30),
        _edge("e26", "party-support", "election-risk", EdgeType.THREATENS, 0.69, "https://www.csds.in", 0.18, 2, ["society"], time_to_impact_days=35),
        _edge("e27", "election-risk", "maharashtra", EdgeType.THREATENS, 0.71, "https://www.csds.in", 0.14, 2, ["society"], time_to_impact_days=35),
        _edge("e28", "election-risk", "madhya-pradesh", EdgeType.THREATENS, 0.68, "https://www.csds.in", 0.14, 2, ["society"], time_to_impact_days=35),
        _edge("e29", "election-risk", "rajasthan", EdgeType.THREATENS, 0.66, "https://www.csds.in", 0.14, 2, ["society"], time_to_impact_days=35),
        _edge("e30", "election-risk", "uttar-pradesh", EdgeType.THREATENS, 0.73, "https://www.csds.in", 0.14, 2, ["society"], time_to_impact_days=35),
        _edge("e31", "election-risk", "bihar", EdgeType.THREATENS, 0.7, "https://www.csds.in", 0.14, 2, ["society"], time_to_impact_days=35),
        _edge("e32", "india-oil-risk", "oil-imports", EdgeType.DEPENDS_ON, 0.83, "https://comtradeplus.un.org", 0.08, 7, ["economics"], time_to_impact_days=1),
        _edge("e33", "semiconductor-imports", "chip-supply", EdgeType.DEPENDS_ON, 0.85, "https://www.nasscom.in", 0.08, 10, ["technology"], time_to_impact_days=5),
        _edge("e34", "water-stress", "global-drought", EdgeType.CORRELATES_WITH, 0.74, "https://earthdata.nasa.gov", 0.12, 15, ["climate"], time_to_impact_days=20),
        _edge("e35", "global-drought", "food-cpi", EdgeType.THREATENS, 0.66, "https://www.noaa.gov", 0.15, 15, ["climate", "economics"], time_to_impact_days=40),
        _edge("e36", "farmer-protests", "india-strategy", EdgeType.THREATENS, 0.63, "https://www.thehindu.com", 0.18, 5, ["society", "india"], time_to_impact_days=40),
        _edge("e37", "fii-outflow", "india-strategy", EdgeType.THREATENS, 0.59, "https://www.bloomberg.com", 0.2, 3, ["economics", "india"], time_to_impact_days=18),
        _edge("e38", "water-stress", "india-strategy", EdgeType.THREATENS, 0.72, "https://www.imd.gov.in", 0.12, 14, ["climate", "india"], time_to_impact_days=45),
        _edge("e39", "lac", "india-strategy", EdgeType.THREATENS, 0.67, "https://www.mea.gov.in", 0.15, 9, ["defense", "india"], time_to_impact_days=25),
        _edge("e40", "semiconductor-imports", "india-it", EdgeType.THREATENS, 0.71, "https://www.nasscom.in", 0.1, 10, ["technology", "india"], time_to_impact_days=30),
        _edge("e41", "brent", "india-oil-risk", EdgeType.CORRELATES_WITH, 0.77, "https://www.worldbank.org", 0.12, 7, ["economics"], time_to_impact_days=3),
        _edge("e42", "monsoon", "food-cpi", EdgeType.CORRELATES_WITH, 0.61, "https://www.imd.gov.in", 0.1, 2, ["climate", "economics"], time_to_impact_days=25),
        _edge("e43", "pakistan-stability", "india-strategy", EdgeType.THREATENS, 0.64, "https://acleddata.com", 0.18, 4, ["defense", "geopolitics"], time_to_impact_days=20),
        _edge("e44", "fed-rate", "rbi-policy", EdgeType.SIGNALS, 0.66, "https://www.rbi.org.in", 0.16, 8, ["economics"], time_to_impact_days=10),
        _edge("e45", "rbi-policy", "food-cpi", EdgeType.STABILIZES, 0.58, "https://www.rbi.org.in", 0.18, 8, ["economics"], time_to_impact_days=45),
    ]
