from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.ingestion.gdelt import fetch_gdelt_events
from app.ingestion.rss import fetch_rss_feeds
from app.ingestion.twitter import fetch_twitter_mentions
from app.limiter import limiter
from app.models.responses import DemoIngestionResponse


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/demo", response_model=DemoIngestionResponse)
@limiter.limit("30/minute")
async def ingest_demo(request: Request) -> DemoIngestionResponse:
    logger.info("API request received %s %s", request.method, request.url.path)
    graph_client = request.app.state.graph_client
    pipeline = request.app.state.pipeline
    upsert = request.app.state.upsert_service

    created_nodes = 0
    created_edges = 0
    seed_nodes = ["india"]

    for runner in (fetch_gdelt_events, fetch_rss_feeds, fetch_twitter_mentions):
        result = await runner(graph_client=graph_client, pipeline=pipeline, upsert_service=upsert)
        created_nodes += int(result.get("created_nodes", 0))
        created_edges += int(result.get("created_edges", 0))
        seed_nodes.extend(result.get("new_node_ids", []))

    graph = graph_client.subgraph(seed_nodes=list(dict.fromkeys(seed_nodes))[:8], max_level=2, min_strength=0.0)
    return DemoIngestionResponse(
        ingested_documents=max(created_nodes, 0),
        created_nodes=created_nodes,
        created_edges=created_edges,
        graph=graph,
    )
