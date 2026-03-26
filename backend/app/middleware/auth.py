from __future__ import annotations

import logging

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings


logger = logging.getLogger(__name__)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/") or request.url.path == "/api/health":
            return await call_next(request)

        provided_key = request.headers.get("X-API-Key")
        if provided_key != settings.argos_api_key:
            logger.warning("Rejected unauthorized request to %s", request.url.path)
            return JSONResponse(status_code=401, content={"error": "Invalid or missing API key"})
        return await call_next(request)
