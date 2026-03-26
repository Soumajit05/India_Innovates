from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

import feedparser

from app.models.entities import IngestionDocument
from app.nlp.events import infer_domain


logger = logging.getLogger(__name__)


RSS_FEEDS = [
    "https://feeds.feedburner.com/ndtvnews-india-news",
    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "https://www.thehindu.com/news/national/feeder/default.rss",
]

SEEN_URLS: set[str] = set()


def _entry_datetime(entry) -> datetime:
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if getattr(entry, "updated_parsed", None):
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


async def fetch_rss_feeds(*, graph_client, pipeline, upsert_service) -> dict[str, object]:
    created_nodes = 0
    created_edges = 0
    new_node_ids: list[str] = []

    for feed_url in RSS_FEEDS:
        try:
            feed = await asyncio.to_thread(feedparser.parse, feed_url)
        except Exception as exc:  # pragma: no cover - network dependent
            logger.error("RSS feed failure for %s: %s", feed_url, exc)
            continue

        for index, entry in enumerate(feed.entries[:10]):
            article_url = getattr(entry, "link", None)
            if not article_url or article_url in SEEN_URLS:
                continue
            SEEN_URLS.add(article_url)
            title = getattr(entry, "title", f"RSS Article {index + 1}")
            summary = getattr(entry, "summary", "")
            published_at = _entry_datetime(entry)
            document = IngestionDocument(
                id=f"rss-{published_at.strftime('%Y%m%d%H%M%S')}-{index}",
                title=title,
                body=summary,
                source_url=article_url,
                source_domain=(urlparse(article_url).hostname or urlparse(feed_url).hostname or "rss"),
                published_at=published_at,
                domain=infer_domain(f"{title}. {summary}"),
                tags=["rss", "live-ingestion", "india"],
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

    return {
        "created_nodes": created_nodes,
        "created_edges": created_edges,
        "new_node_ids": new_node_ids,
    }
