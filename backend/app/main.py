from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api import alerts, dashboard, feedback, graph, ingest, query, scenarios
from app.config import settings
from app.graph.neo4j_client import InMemoryNeo4jClient
from app.graph.seed import seeded_edges, seeded_nodes
from app.graph.upsert import GraphUpsertService
from app.ingestion.gdelt import fetch_gdelt_events
from app.ingestion.rss import fetch_rss_feeds
from app.ingestion.worldbank import fetch_worldbank_indicators
from app.limiter import limiter
from app.middleware.auth import APIKeyAuthMiddleware
from app.models.responses import AlertItem
from app.nlp.pipeline import NLPPipeline
from app.reasoning.rag import GraphRAGService
from app.reasoning.scenario import ScenarioSimulator


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry_after = "60"
    headers = getattr(exc, "headers", {}) or {}
    if "Retry-After" in headers:
        retry_after = str(headers["Retry-After"])
    return JSONResponse(
        status_code=429,
        content={"error": f"Rate limit exceeded. Retry after {retry_after}s"},
        headers=headers,
    )


async def _run_recurring_task(task_name: str, interval_seconds: int, job, app: FastAPI) -> None:
    while True:
        try:
            result = await job()
            new_nodes = int(result.get("created_nodes", result.get("new_nodes", 0)))
            logger.info("Scheduled task: %s completed, %s new nodes added", task_name, new_nodes)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Scheduled task %s failed: %s", task_name, exc)
        await asyncio.sleep(interval_seconds)


def _build_app_state(app: FastAPI) -> None:
    graph_client = InMemoryNeo4jClient()
    upsert_service = GraphUpsertService(graph_client)
    upsert_service.load_seed_graph(seeded_nodes(), seeded_edges())

    app.state.graph_client = graph_client
    app.state.upsert_service = upsert_service
    app.state.pipeline = NLPPipeline(graph_client)
    app.state.rag_service = GraphRAGService(graph_client)
    app.state.scenario_service = ScenarioSimulator(graph_client)
    app.state.feedback_store = []

    def build_alerts() -> list[AlertItem]:
        nodes = graph_client.list_nodes()
        edges = graph_client.list_edges()
        lookup = {node.id: node for node in nodes}
        high_edges = [edge for edge in edges if edge.current_strength >= 0.65][:8]
        alerts_list: list[AlertItem] = []
        for edge in high_edges:
            if edge.source not in lookup or edge.target not in lookup:
                continue
            alerts_list.append(
                AlertItem(
                    id=f"alert-{edge.id}",
                    title=f"{lookup[edge.source].name} {edge.type.value.replace('_', ' ')} {lookup[edge.target].name}",
                    summary=(
                        f"Confidence {edge.current_strength:.2f} with source credibility {edge.source_credibility:.2f}. "
                        f"Tagged domains: {', '.join(edge.tags)}."
                    ),
                    domain=lookup[edge.target].domain,
                    severity=min(1.0, round(edge.current_strength + 0.08, 2)),
                    source_url=edge.source_url,
                    created_at=edge.updated_at if edge.updated_at.tzinfo else edge.updated_at.replace(tzinfo=timezone.utc),
                    affected_entities=[lookup[edge.source].name, lookup[edge.target].name],
                )
            )
        return alerts_list

    app.state.build_alerts = build_alerts


def create_app(testing: bool = False) -> FastAPI:
    configure_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        tasks: list[asyncio.Task] = []
        if not testing:
            interval_seconds = settings.scheduler_interval_minutes * 60
            recompute_seconds = settings.recompute_interval_minutes * 60

            tasks.append(
                asyncio.create_task(
                    _run_recurring_task(
                        "fetch_worldbank_indicators",
                        interval_seconds,
                        lambda: fetch_worldbank_indicators(upsert_service=app.state.upsert_service),
                        app,
                    )
                )
            )
            tasks.append(
                asyncio.create_task(
                    _run_recurring_task(
                        "fetch_gdelt_events",
                        interval_seconds,
                        lambda: fetch_gdelt_events(
                            graph_client=app.state.graph_client,
                            pipeline=app.state.pipeline,
                            upsert_service=app.state.upsert_service,
                        ),
                        app,
                    )
                )
            )
            tasks.append(
                asyncio.create_task(
                    _run_recurring_task(
                        "fetch_rss_feeds",
                        interval_seconds,
                        lambda: fetch_rss_feeds(
                            graph_client=app.state.graph_client,
                            pipeline=app.state.pipeline,
                            upsert_service=app.state.upsert_service,
                        ),
                        app,
                    )
                )
            )
            tasks.append(
                asyncio.create_task(
                    _run_recurring_task(
                        "recompute_all_edge_strengths",
                        recompute_seconds,
                        lambda: asyncio.to_thread(
                            lambda: {"created_nodes": 0, "edges_recomputed": app.state.graph_client.recompute_all_edge_strengths()}
                        ),
                        app,
                    )
                )
            )

        app.state.background_tasks = tasks
        yield
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    _build_app_state(app)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://localhost:3000", "http://127.0.0.1:3011"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(APIKeyAuthMiddleware)

    @app.middleware("http")
    async def log_api_requests(request: Request, call_next):
        if request.url.path.startswith("/api/"):
            logger.info("API request received %s %s", request.method, request.url.path)
        return await call_next(request)

    @app.get(f"{settings.api_prefix}/health")
    async def healthcheck() -> dict[str, object]:
        graph_client = app.state.graph_client
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "graph_mode": "in-memory",
            "node_count": len(graph_client.list_nodes()),
            "edge_count": len(graph_client.list_edges()),
        }

    app.include_router(dashboard.router, prefix=settings.api_prefix)
    app.include_router(query.router, prefix=settings.api_prefix)
    app.include_router(graph.router, prefix=settings.api_prefix)
    app.include_router(alerts.router, prefix=settings.api_prefix)
    app.include_router(scenarios.router, prefix=settings.api_prefix)
    app.include_router(ingest.router, prefix=settings.api_prefix)
    app.include_router(feedback.router, prefix=settings.api_prefix)
    return app


app = create_app()
