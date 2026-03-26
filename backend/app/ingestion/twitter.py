from __future__ import annotations

import logging

import httpx

from app.config import settings


logger = logging.getLogger(__name__)


TWITTER_KEYWORDS = [
    "India LAC",
    "QUAD",
    "India China",
    "India Pakistan",
    "RBI rate",
    "India defense",
]


async def fetch_twitter_mentions(*, graph_client=None, pipeline=None, upsert_service=None) -> dict[str, object]:
    if not settings.twitter_bearer_token:
        logger.info("Twitter connector disabled — no TWITTER_BEARER_TOKEN set. Add token to .env to enable.")
        return {"created_nodes": 0, "created_edges": 0, "new_node_ids": []}

    headers = {"Authorization": f"Bearer {settings.twitter_bearer_token}"}
    rules_url = "https://api.twitter.com/2/tweets/search/stream/rules"
    stream_url = "https://api.twitter.com/2/tweets/search/stream"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            existing_rules_response = await client.get(rules_url, headers=headers)
            existing_rules_response.raise_for_status()
            existing_rules = existing_rules_response.json().get("data", [])
            existing_values = {rule.get("value") for rule in existing_rules}
            add_rules = [{"value": keyword} for keyword in TWITTER_KEYWORDS if keyword not in existing_values]
            if add_rules:
                await client.post(rules_url, headers=headers, json={"add": add_rules})

            tweets: list[dict[str, object]] = []
            async with client.stream(
                "GET",
                stream_url,
                headers=headers,
                params={"tweet.fields": "created_at,text"},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    tweets.append({"raw": line})
                    if len(tweets) >= 5:
                        break

        logger.info("Twitter connector fetched %s live stream messages", len(tweets))
        return {"created_nodes": 0, "created_edges": 0, "new_node_ids": []}
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("Twitter connector failure: %s", exc)
        return {"created_nodes": 0, "created_edges": 0, "new_node_ids": []}
