from __future__ import annotations

from fastapi import APIRouter, Response
from pulsecheck.core import HealthRegistry, http_status_from_health


def make_health_router(registry: HealthRegistry, *, prefix: str = "/health") -> APIRouter:
    router = APIRouter(prefix=prefix, tags=["Health"])

    @router.get("")
    async def health() -> Response:
        res = registry.liveness()
        return Response(
            content=_json(res.to_dict()),
            status_code=http_status_from_health(res.status),
            media_type="application/json",
        )

    @router.get("/live")
    async def live() -> Response:
        res = registry.liveness()
        return Response(
            content=_json(res.to_dict()),
            status_code=http_status_from_health(res.status),
            media_type="application/json",
        )

    @router.get("/ready")
    async def ready() -> Response:
        res = await registry.readiness()
        return Response(
            content=_json(res.to_dict()),
            status_code=http_status_from_health(res.status),
            media_type="application/json",
        )

    return router


def _json(payload: dict) -> str:
    # avoid adding pydantic dependency in the lib
    import json
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
