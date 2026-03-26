from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from app.config import settings
from app.models.entities import IngestionDocument
from app.nlp.events import infer_domain


logger = logging.getLogger(__name__)


def _parse_gdelt_datetime(raw_value: str | None) -> datetime:
    if not raw_value:
        return datetime.now(timezone.utc)
    try:
        return datetime.strptime(raw_value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


async def fetch_gdelt_events(*, graph_client, pipeline, upsert_service, http_client: httpx.AsyncClient | None = None) -> dict[str, object]:
    created_nodes = 0
    created_edges = 0
    new_node_ids: list[str] = []
    params = {
        "query": "India",
        "mode": "artlist",
        "maxrecords": 10,
        "format": "json",
    }
    client = http_client or httpx.AsyncClient(timeout=10.0)
    should_close = http_client is None

    try:
        try:
            response = await client.get(settings.gdelt_api_base, params=params)
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:  # pragma: no cover - network dependent
            logger.error("GDELT API failure: %s", exc)
            return {"created_nodes": 0, "created_edges": 0, "new_node_ids": []}

        articles = payload.get("articles", [])
        for index, article in enumerate(articles):
            url = article.get("url") or article.get("sourceurl")
            if not url:
                continue
            title = article.get("title") or article.get("seendate") or f"GDELT Article {index + 1}"
            body = article.get("snippet") or article.get("title") or ""
            published_at = _parse_gdelt_datetime(article.get("seendate"))
            domain = infer_domain(f"{title}. {body}")
            document = IngestionDocument(
                id=f"gdelt-{published_at.strftime('%Y%m%d%H%M%S')}-{index}",
                title=title,
                body=body,
                source_url=url,
                source_domain=(urlparse(url).hostname or "gdeltproject.org"),
                published_at=published_at,
                domain=domain,
                tags=["gdelt", "live-ingestion", "india"],
                metadata={"gdelt_url": response.url.__str__()},
            )
            result = pipeline.run(document)
            related_node_ids: list[str] = []
            for entity in result.entities:
                matches = graph_client.search_nodes(entity.text)
                if matches:
                    related_node_ids.append(matches[0].id)
            if not related_node_ids:
                related_node_ids.append("india")
            node_count, edge_count = upsert_service.upsert_document_event(document, list(dict.fromkeys(related_node_ids[:5])))
            created_nodes += node_count
            created_edges += edge_count
            new_node_ids.append(document.id)
    finally:
        if should_close:
            await client.aclose()

    return {
        "created_nodes": created_nodes,
        "created_edges": created_edges,
        "new_node_ids": new_node_ids,
    }
