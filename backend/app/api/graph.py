from __future__ import annotations

import logging

from fastapi import APIRouter, Query, Request

from app.limiter import limiter
from app.models.entities import EdgeType
from app.models.responses import GraphExplorerResponse


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/explorer", response_model=GraphExplorerResponse)
@limiter.limit("30/minute")
def graph_explorer(
    request: Request,
    domains: list[str] | None = Query(default=None),
    edge_types: list[EdgeType] | None = Query(default=None),
    min_confidence: float = 0.25,
    search: str | None = None,
) -> GraphExplorerResponse:
    logger.info("API request received %s %s", request.method, request.url.path)
    graph_client = request.app.state.graph_client
    nodes = graph_client.list_nodes()
    if domains:
        allowed_domains = set(domains)
        nodes = [node for node in nodes if node.domain.value in allowed_domains]
    if search:
        terms = search.lower()
        nodes = [
            node
            for node in nodes
            if terms in node.name.lower() or any(terms in str(alias).lower() for alias in node.properties.get("aliases", []))
        ]
    node_ids = [node.id for node in nodes[:12]]
    graph = graph_client.subgraph(
        seed_nodes=node_ids or [node.id for node in graph_client.list_nodes()[:4]],
        max_level=2,
        allowed_edge_types=set(edge_types) if edge_types else None,
        min_strength=min_confidence,
    )
    return GraphExplorerResponse(graph=graph)


@router.get("/subgraph/{node_id}", response_model=GraphExplorerResponse)
@limiter.limit("30/minute")
def graph_subgraph(request: Request, node_id: str, max_level: int = 3) -> GraphExplorerResponse:
    logger.info("API request received %s %s node='%s'", request.method, request.url.path, node_id)
    graph_client = request.app.state.graph_client
    node = graph_client.get_node(node_id) or graph_client.get_node_by_name(node_id)
    graph = graph_client.subgraph(seed_nodes=[node.id if node else node_id], max_level=max_level, min_strength=0.0)
    return GraphExplorerResponse(graph=graph)
