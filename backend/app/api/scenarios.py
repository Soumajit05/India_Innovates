from __future__ import annotations

import logging

from fastapi import APIRouter, Body, HTTPException, Request

from app.limiter import limiter
from app.models.responses import ScenarioRequest, ScenarioResponse


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("/templates")
@limiter.limit("30/minute")
def get_scenario_templates(request: Request) -> list[dict[str, object]]:
    logger.info("API request received %s %s", request.method, request.url.path)
    return [
        {"trigger_node": "US Fed Funds Rate", "change_percent": 50, "label": "US Fed Rate Hike -> India Farmer Distress"},
        {"trigger_node": "Taiwan Strait Conflict", "change_percent": 60, "label": "Taiwan Blockade -> India Tech Sector"},
        {"trigger_node": "Pakistan Stability Index", "change_percent": -35, "label": "Pakistan Instability -> Border Security"},
        {"trigger_node": "IMD Monsoon Forecast", "change_percent": -12, "label": "Below-Normal Monsoon -> Electoral Risk"},
    ]


@router.post("/simulate", response_model=ScenarioResponse)
@limiter.limit("5/minute")
def simulate_scenario(request: Request, payload: dict = Body(...)) -> ScenarioResponse:
    scenario_payload = ScenarioRequest.model_validate(payload)
    logger.info("API request received %s %s trigger='%s'", request.method, request.url.path, scenario_payload.trigger_node[:120])
    try:
        return request.app.state.scenario_service.simulate(
            scenario_payload.trigger_node,
            scenario_payload.change_percent,
            depth=scenario_payload.depth,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
