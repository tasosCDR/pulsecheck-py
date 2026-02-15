from __future__ import annotations

import time
import redis  # type: ignore

from ..models import HealthCheckResult, HealthStatus
from ..utils import now_ms, to_thread, with_timeout
from .base import CheckConfig, HealthCheck


class RedisSyncCheck(HealthCheck):
    def __init__(self, redis_url: str, *, name: str = "redis", timeout_s: float = 2.0, degrade_threshold_ms: float = 100.0) -> None:
        super().__init__(CheckConfig(name=name, readiness=True, timeout_s=timeout_s, degrade_threshold_ms=degrade_threshold_ms))
        self._url = redis_url

    async def check(self) -> HealthCheckResult:
        start = time.perf_counter()

        def _sync() -> None:
            client = redis.from_url(self._url, socket_timeout=self.config.timeout_s)
            try:
                client.ping()
            finally:
                try:
                    client.close()
                except Exception:
                    pass

        try:
            await with_timeout(to_thread(_sync), self.config.timeout_s)
            elapsed = now_ms(start)
            status = HealthStatus.DEGRADED if (self.config.degrade_threshold_ms and elapsed > self.config.degrade_threshold_ms) else HealthStatus.HEALTHY
            return HealthCheckResult(status=status, response_time_ms=elapsed)
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"Redis failed: {repr(e)}")
