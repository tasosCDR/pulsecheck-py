from __future__ import annotations

from django.http import JsonResponse  # type: ignore
from pulsecheck_py.core import HealthRegistry, http_status_from_health


def make_views(registry: HealthRegistry):
    def health(request):
        res = registry.liveness()
        return JsonResponse(res.to_dict(), status=http_status_from_health(res.status))

    async def ready(request):
        res = await registry.readiness()
        return JsonResponse(res.to_dict(), status=http_status_from_health(res.status))

    return health, ready
