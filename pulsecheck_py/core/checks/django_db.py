from __future__ import annotations

import time
from django.db import connection  # type: ignore

from ..models import HealthCheckResult, HealthStatus
from ..utils import now_ms, to_thread, with_timeout
from .base import CheckConfig, HealthCheck


class DjangoDBCheck(HealthCheck):
    def __init__(self, *, name: str = "database", timeout_s: float = 2.0, degrade_threshold_ms: float = 500.0) -> None:
        super().__init__(CheckConfig(name=name, readiness=True, timeout_s=timeout_s, degrade_threshold_ms=degrade_threshold_ms))

    async def check(self) -> HealthCheckResult:
        start = time.perf_counter()

        def _sync() -> None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        try:
            await with_timeout(to_thread(_sync), self.config.timeout_s)
            elapsed = now_ms(start)
            status = HealthStatus.DEGRADED if (self.config.degrade_threshold_ms and elapsed > self.config.degrade_threshold_ms) else HealthStatus.HEALTHY
            return HealthCheckResult(status=status, response_time_ms=elapsed)
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"Django DB failed: {repr(e)}")
