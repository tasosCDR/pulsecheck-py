from __future__ import annotations

import time
from celery import Celery  # type: ignore

from ..models import HealthCheckResult, HealthStatus
from ..utils import now_ms, to_thread, with_timeout
from .base import CheckConfig, HealthCheck


class CeleryInspectCheck(HealthCheck):
    def __init__(
        self,
        celery_app: Celery,
        *,
        name: str = "celery",
        timeout_s: float = 3.0,
        degrade_threshold_ms: float = 1200.0,
        require_workers: bool = True,
    ) -> None:
        super().__init__(CheckConfig(name=name, readiness=True, timeout_s=timeout_s, degrade_threshold_ms=degrade_threshold_ms))
        self._celery = celery_app
        self._require_workers = require_workers

    async def check(self) -> HealthCheckResult:
        start = time.perf_counter()

        def _sync() -> None:
            inspect = self._celery.control.inspect(timeout=min(2.0, self.config.timeout_s))
            ping = inspect.ping()
            if self._require_workers and not ping:
                raise RuntimeError("No Celery workers responding")

        try:
            await with_timeout(to_thread(_sync), self.config.timeout_s)
            elapsed = now_ms(start)
            status = HealthStatus.DEGRADED if (self.config.degrade_threshold_ms and elapsed > self.config.degrade_threshold_ms) else HealthStatus.HEALTHY
            return HealthCheckResult(status=status, response_time_ms=elapsed)
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"Celery failed: {repr(e)}")
