from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.limiter import limiter
from app.models.responses import AlertItem


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertItem])
@limiter.limit("30/minute")
def get_alerts(request: Request) -> list[AlertItem]:
    logger.info("API request received %s %s", request.method, request.url.path)
    return request.app.state.build_alerts()
