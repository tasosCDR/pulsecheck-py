from __future__ import annotations

import http
from .models import HealthStatus


def http_status_from_health(status: HealthStatus) -> int:
    # Same behavior you already use:
    # - HEALTHY/DEGRADED => 200
    # - UNHEALTHY => 503
    if status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED):
        return int(http.HTTPStatus.OK)
    return int(http.HTTPStatus.SERVICE_UNAVAILABLE)


def combine_status(current: HealthStatus, incoming: HealthStatus) -> HealthStatus:
    """
    HEALTHY + DEGRADED => DEGRADED
    Any UNHEALTHY => UNHEALTHY
    """
    if current == HealthStatus.UNHEALTHY or incoming == HealthStatus.UNHEALTHY:
        return HealthStatus.UNHEALTHY
    if current == HealthStatus.DEGRADED or incoming == HealthStatus.DEGRADED:
        return HealthStatus.DEGRADED
    return HealthStatus.HEALTHY
