from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request

from app.graph.ontology import DOMAIN_ORDER
from app.limiter import limiter
from app.models.entities import EdgeType
from app.models.responses import AlertItem, Citation, DashboardMetric, DashboardOverview, DomainMatrixCell, IndiaRiskState


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def calculate_india_risk_score(graph_client) -> tuple[float, dict[str, float], list[Citation]]:
    india = graph_client.get_node("india") or graph_client.get_node_by_name("India")
    if not india:
        return 0.0, {}, []

    node_lookup = {node.id: node for node in graph_client.list_nodes()}
    contributions: list[tuple[str, float, object]] = []

    for edge in graph_client.list_edges():
        if edge.type not in {EdgeType.THREATENS, EdgeType.DEPENDS_ON, EdgeType.CAUSES}:
            continue
        if india.id not in {edge.source, edge.target}:
            continue

        contribution = 0.0
        if edge.type == EdgeType.THREATENS:
            severity = float(edge.properties.get("severity", 0.5))
            contribution = severity * edge.current_strength
        elif edge.type == EdgeType.DEPENDS_ON:
            dependency_pct = float(edge.properties.get("dependency_pct", edge.properties.get("severity", 0.6) * 100))
            contribution = (dependency_pct / 100.0) * edge.current_strength * 0.5
        elif edge.type == EdgeType.CAUSES and edge.target == india.id and edge.properties.get("negative_effect", False):
            contribution = edge.confidence * edge.current_strength * 0.3

        if contribution <= 0:
            continue

        label = f"{node_lookup.get(edge.source).name if edge.source in node_lookup else edge.source} -> {edge.type.value} -> {node_lookup.get(edge.target).name if edge.target in node_lookup else edge.target}"
        contributions.append((label, contribution, edge))

    contributions.sort(key=lambda item: item[1], reverse=True)
    normalized_score = min(100.0, round(sum(item[1] for item in contributions) * 20, 1))
    risk_breakdown = {label: round(score * 20, 1) for label, score, _ in contributions[:5]}
    top_vulnerabilities = [
        Citation(
            edge_id=edge.id,
            label=label,
            source_url=edge.source_url,
            confidence=edge.confidence,
            strength=edge.current_strength,
        )
        for label, _, edge in contributions[:5]
    ]
    return normalized_score, risk_breakdown, top_vulnerabilities


@router.get("/overview", response_model=DashboardOverview)
@limiter.limit("30/minute")
def get_dashboard_overview(request: Request) -> DashboardOverview:
    logger.info("API request received %s %s", request.method, request.url.path)
    graph_client = request.app.state.graph_client
    nodes = graph_client.list_nodes()
    edges = graph_client.list_edges()
    alerts: list[AlertItem] = request.app.state.build_alerts()

    matrix_counter: Counter[tuple[object, object]] = Counter()
    node_lookup = {node.id: node for node in nodes}
    for edge in edges:
        if edge.source in node_lookup and edge.target in node_lookup:
            source_domain = node_lookup[edge.source].domain
            target_domain = node_lookup[edge.target].domain
            matrix_counter[(source_domain, target_domain)] += 1

    matrix = [
        DomainMatrixCell(
            from_domain=from_domain,
            to_domain=to_domain,
            value=matrix_counter.get((from_domain, to_domain), 0),
        )
        for from_domain in DOMAIN_ORDER
        for to_domain in DOMAIN_ORDER
    ]

    india_risk_overlay = [
        IndiaRiskState(
            state=node.name,
            score=float(node.properties.get("state_risk", 0.0)),
            driver="Electoral stress + monsoon sensitivity",
        )
        for node in nodes
        if "state_risk" in node.properties
    ]
    india_risk_overlay.sort(key=lambda item: item.score, reverse=True)
    india_risk_score, risk_breakdown, top_vulnerabilities = calculate_india_risk_score(graph_client)
    recent_cutoff = datetime.now(timezone.utc) - timedelta(days=1)

    metrics = [
        DashboardMetric(label="Total Nodes", value=str(len(nodes)), delta="+live"),
        DashboardMetric(
            label="Edges In Last 24h",
            value=str(sum(1 for edge in edges if edge.created_at >= recent_cutoff)),
            delta="dynamic",
        ),
        DashboardMetric(label="Active Alerts", value=str(len(alerts)), delta="live"),
        DashboardMetric(label="India Risk Score", value=str(india_risk_score), delta="Dynamic"),
    ]

    return DashboardOverview(
        metrics=metrics,
        domain_matrix=matrix,
        alerts=alerts[:5],
        india_risk_overlay=india_risk_overlay[:5],
        top_vulnerabilities=top_vulnerabilities,
        risk_breakdown=risk_breakdown,
    )
