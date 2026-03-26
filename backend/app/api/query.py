from __future__ import annotations

import json
import logging
import time
import uuid

from fastapi import APIRouter, Body, Query, Request
from fastapi.responses import StreamingResponse

from app.limiter import limiter
from app.models.responses import CausalChainResponse, QueryRequest, QueryResponse
from app.reasoning.evaluation import evaluate_grounding
from app.reasoning.synthesis import (
    ARGOS_SYSTEM_PROMPT,
    MODEL_NAME,
    build_citations,
    build_llm_prompt,
    get_anthropic_client,
    synthesize_query,
)


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/query", tags=["query"])


def _prepare_query_context(request: Request, payload: QueryRequest):
    rag_service = request.app.state.rag_service
    subgraph, matched_nodes = rag_service.retrieve_subgraph(
        payload.query,
        max_hops=payload.max_hops,
        confidence_threshold=payload.confidence_threshold,
    )
    chain = rag_service.find_chain_for_query(payload.query, matched_nodes)
    node_lookup = {node.id: node for node in subgraph.nodes}
    citations = build_citations(subgraph.edges, node_lookup)
    contradictions = [
        f"{edge.properties.get('field', 'value')}: {edge.properties.get('value_a')} vs {edge.properties.get('value_b')}"
        for edge in subgraph.edges
        if edge.type.value == "CONTRADICTS"
    ]
    stale_edges = [edge.id for edge in subgraph.edges if edge.is_stale]
    if stale_edges:
        logger.warning("Stale edges used in query '%s': %s", payload.query[:80], ", ".join(stale_edges))
    return subgraph, matched_nodes, chain, citations, contradictions


async def _build_query_response(request: Request, payload: QueryRequest) -> QueryResponse:
    query_id = str(uuid.uuid4())
    start = time.perf_counter()
    logger.info("API request received %s %s query='%s'", request.method, request.url.path, payload.query[:120])
    subgraph, matched_nodes, chain, citations, contradictions = _prepare_query_context(request, payload)
    synthesis_text, brief, llm_fallback_used, warning = await synthesize_query(
        query=payload.query,
        subgraph=subgraph,
        citations=citations,
        chain=chain,
        contradictions=contradictions,
    )

    causal_chain = None
    if chain:
        causal_chain = CausalChainResponse(
            nodes=chain.nodes,
            edges=chain.edges,
            chain_confidence=chain.chain_confidence,
            path=chain.path,
            explanation=(
                f"The chain from {chain.nodes[0].name} to {chain.nodes[-1].name} passes through "
                f"{len(chain.edges)} live-decayed hops."
            ),
            time_to_impact_days=chain.time_to_impact_days,
            warnings=chain.warnings,
        )

    grounding = evaluate_grounding(
        synthesis_text,
        cited_nodes=[node.name for node in subgraph.nodes],
        cited_edges=[edge.type.value for edge in subgraph.edges],
    )

    return QueryResponse(
        query_id=query_id,
        synthesis=synthesis_text,
        brief=brief,
        citations=citations,
        subgraph=subgraph,
        causal_chain=causal_chain,
        contradictions=contradictions,
        grounding_rate=float(grounding["grounding_rate"]),
        grounding_details=grounding,
        llm_fallback_used=llm_fallback_used,
        warning=warning,
        query_time_ms=round((time.perf_counter() - start) * 1000),
    )


@router.post("", response_model=QueryResponse)
@limiter.limit("10/minute")
async def query_graph(request: Request, payload: dict = Body(...)) -> QueryResponse:
    return await _build_query_response(request, QueryRequest.model_validate(payload))


async def _fallback_stream(payload: QueryRequest, request: Request):
    response = await _build_query_response(request, payload)
    for token in response.synthesis.split():
        yield json.dumps({"type": "text", "content": f"{token} "}) + "\n"
    yield json.dumps(
        {
            "type": "citations",
            "nodes": [citation.model_dump(mode="json") for citation in response.citations],
            "subgraph": response.subgraph.model_dump(mode="json"),
            "query_time_ms": response.query_time_ms,
        }
    ) + "\n"


async def _stream_query_response(request: Request, payload: QueryRequest):
    start = time.perf_counter()
    logger.info("API request received %s %s query='%s'", request.method, request.url.path, payload.query[:120])
    subgraph, matched_nodes, chain, citations, contradictions = _prepare_query_context(request, payload)
    client = get_anthropic_client()
    prompt = build_llm_prompt(query=payload.query, subgraph=subgraph, chain=chain, contradictions=contradictions)

    if client is None:
        async for chunk in _fallback_stream(payload, request):
            yield chunk
        return

    try:
        async with client.messages.stream(
            model=MODEL_NAME,
            max_tokens=1500,
            system=ARGOS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for token in stream.text_stream:
                yield json.dumps({"type": "text", "content": token}) + "\n"

        yield json.dumps(
            {
                "type": "citations",
                "nodes": [citation.model_dump(mode="json") for citation in citations],
                "subgraph": subgraph.model_dump(mode="json"),
                "query_time_ms": round((time.perf_counter() - start) * 1000),
            }
        ) + "\n"
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("Stream failure for query '%s': %s", payload.query[:80], exc)
        yield json.dumps({"type": "error", "message": "Stream interrupted"}) + "\n"


@router.get("/stream")
@limiter.limit("10/minute")
async def stream_query_get(
    request: Request,
    query: str = Query(...),
    max_hops: int = Query(default=3, ge=1, le=5),
    confidence_threshold: float = Query(default=0.25, ge=0.0, le=1.0),
) -> StreamingResponse:
    payload = QueryRequest(query=query, max_hops=max_hops, confidence_threshold=confidence_threshold)
    return StreamingResponse(_stream_query_response(request, payload), media_type="text/event-stream")


@router.post("/stream")
@limiter.limit("10/minute")
async def stream_query_post(request: Request, payload: dict = Body(...)) -> StreamingResponse:
    query_payload = QueryRequest.model_validate(payload)
    return StreamingResponse(_stream_query_response(request, query_payload), media_type="text/event-stream")
