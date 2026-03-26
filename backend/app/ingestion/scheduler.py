from __future__ import annotations

from app.ingestion import gdelt, rss, twitter, worldbank
from app.models.entities import IngestionDocument


class DemoIngestionScheduler:
    def collect_documents(self, batch_size: int = 3) -> list[IngestionDocument]:
        documents = [
            *gdelt.fetch_demo_documents(),
            *worldbank.fetch_demo_documents(),
            *rss.fetch_demo_documents(),
            *twitter.fetch_demo_documents(),
        ]
        documents.sort(key=lambda item: item.published_at, reverse=True)
        return documents[:batch_size]
