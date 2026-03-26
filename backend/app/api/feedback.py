from __future__ import annotations

import logging

from fastapi import APIRouter, Body, Request

from app.limiter import limiter
from app.models.responses import FeedbackRequest, FeedbackStatsResponse


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("")
@limiter.limit("30/minute")
def submit_feedback(request: Request, payload: dict = Body(...)) -> dict[str, object]:
    feedback_payload = FeedbackRequest.model_validate(payload)
    logger.info("API request received %s %s query_id='%s'", request.method, request.url.path, feedback_payload.query_id)
    feedback_store: list[dict[str, object]] = request.app.state.feedback_store
    feedback_store.append(feedback_payload.model_dump())

    graph_client = request.app.state.graph_client
    for edge_id in feedback_payload.flagged_edge_ids:
        edge = graph_client.lower_edge_confidence(edge_id, delta=0.1)
        if edge:
            logger.info("Feedback flagged edge %s; confidence reduced to %.2f", edge_id, edge.confidence)
    for node_id in feedback_payload.cited_node_ids:
        node = graph_client.boost_node_relevance(node_id, delta=0.1)
        if node:
            logger.info("Feedback boosted node %s relevance to %.2f", node_id, float(node.properties.get("relevance_score", 0.0)))

    return {"status": "ok", "stored_feedback": len(feedback_store)}


@router.get("/stats", response_model=FeedbackStatsResponse)
@limiter.limit("30/minute")
def feedback_stats(request: Request) -> FeedbackStatsResponse:
    logger.info("API request received %s %s", request.method, request.url.path)
    feedback_store: list[dict[str, object]] = request.app.state.feedback_store
    total_queries_rated = len(feedback_store)
    average_rating = round(
        sum(int(item["rating"]) for item in feedback_store) / total_queries_rated,
        2,
    ) if total_queries_rated else 0.0
    total_edges_flagged = sum(len(item.get("flagged_edge_ids", [])) for item in feedback_store)
    total_nodes_cited = sum(len(item.get("cited_node_ids", [])) for item in feedback_store)
    return FeedbackStatsResponse(
        total_queries_rated=total_queries_rated,
        average_rating=average_rating,
        total_edges_flagged=total_edges_flagged,
        total_nodes_cited=total_nodes_cited,
    )
