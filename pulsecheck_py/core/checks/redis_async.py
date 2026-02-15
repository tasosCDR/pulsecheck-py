from __future__ import annotations

import time
import redis.asyncio as redis  # type: ignore

from ..models import HealthCheckResult, HealthStatus
from ..utils import now_ms, with_timeout
from .base import CheckConfig, HealthCheck


class RedisAsyncCheck(HealthCheck):
    def __init__(self, redis_url: str, *, name: str = "redis", timeout_s: float = 2.0, degrade_threshold_ms: float = 100.0) -> None:
        super().__init__(CheckConfig(name=name, readiness=True, timeout_s=timeout_s, degrade_threshold_ms=degrade_threshold_ms))
        self._url = redis_url

    async def check(self) -> HealthCheckResult:
        start = time.perf_counter()
        client = redis.from_url(self._url, socket_timeout=self.config.timeout_s)

        try:
            await with_timeout(client.ping(), self.config.timeout_s)
            elapsed = now_ms(start)
            status = HealthStatus.DEGRADED if (self.config.degrade_threshold_ms and elapsed > self.config.degrade_threshold_ms) else HealthStatus.HEALTHY
            return HealthCheckResult(status=status, response_time_ms=elapsed)
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"Redis failed: {repr(e)}")
        finally:
            try:
                await client.aclose()
            except Exception:
                pass
