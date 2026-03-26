from __future__ import annotations

import logging

import httpx

from app.config import settings


logger = logging.getLogger(__name__)


WORLD_BANK_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": {"name": "GDP growth rate", "unit": "%"},
    "FP.CPI.TOTL.ZG": {"name": "Inflation (CPI)", "unit": "%"},
    "BN.CAB.XOKA.GD.ZS": {"name": "Current account balance % GDP", "unit": "% of GDP"},
    "DT.ODA.ALLD.GD.ZS": {"name": "External debt", "unit": "% of GNI"},
    "SL.UEM.TOTL.ZS": {"name": "Unemployment rate", "unit": "%"},
}


async def fetch_worldbank_indicators(*, upsert_service, http_client: httpx.AsyncClient | None = None) -> dict[str, object]:
    created_nodes = 0
    created_edges = 0
    new_node_ids: list[str] = []
    client = http_client or httpx.AsyncClient(timeout=10.0)
    should_close = http_client is None

    try:
        for indicator_code, descriptor in WORLD_BANK_INDICATORS.items():
            url = f"{settings.worldbank_api_base}/country/IN/indicator/{indicator_code}?format=json&mrv=1"
            try:
                response = await client.get(url)
                response.raise_for_status()
                payload = response.json()
                latest = payload[1][0] if isinstance(payload, list) and len(payload) > 1 and payload[1] else {}
                value = latest.get("value")
                period = str(latest.get("date", "unknown"))
                unit = latest.get("unit") or descriptor["unit"]
                indicator_id = f"worldbank-{indicator_code.lower().replace('.', '-')}"
                node_count, edge_count = upsert_service.upsert_indicator(
                    indicator_id=indicator_id,
                    indicator_name=descriptor["name"],
                    value=value,
                    unit=unit,
                    period=period,
                    source_url=url,
                )
                created_nodes += node_count
                created_edges += edge_count
                new_node_ids.append(indicator_id)
            except Exception as exc:  # pragma: no cover - network dependent
                logger.error("World Bank API failure for %s: %s", indicator_code, exc)
                continue
    finally:
        if should_close:
            await client.aclose()

    return {
        "created_nodes": created_nodes,
        "created_edges": created_edges,
        "new_node_ids": new_node_ids,
    }
