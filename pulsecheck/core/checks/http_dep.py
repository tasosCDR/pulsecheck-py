from __future__ import annotations

import time
from typing import Optional

import httpx  # type: ignore

from ..models import HealthCheckResult, HealthStatus
from ..utils import now_ms, with_timeout
from .base import CheckConfig, HealthCheck


class HttpDependencyCheck(HealthCheck):
    def __init__(
        self,
        url: str,
        *,
        name: str,
        timeout_s: float = 2.0,
        degrade_threshold_ms: float = 500.0,
        expected_status: int = 200,
        headers: Optional[dict] = None,
    ) -> None:
        super().__init__(CheckConfig(name=name, readiness=True, timeout_s=timeout_s, degrade_threshold_ms=degrade_threshold_ms))
        self._url = url
        self._expected = expected_status
        self._headers = headers or {}

    async def check(self) -> HealthCheckResult:
        start = time.perf_counter()

        async def _run() -> int:
            async with httpx.AsyncClient(timeout=self.config.timeout_s, headers=self._headers) as client:
                resp = await client.get(self._url)
                return resp.status_code

        try:
            code = await with_timeout(_run(), self.config.timeout_s + 0.5)
            elapsed = now_ms(start)
            if code != self._expected:
                return HealthCheckResult(status=HealthStatus.UNHEALTHY, response_time_ms=elapsed, error=f"HTTP {code} (expected {self._expected})")
            status = HealthStatus.DEGRADED if (self.config.degrade_threshold_ms and elapsed > self.config.degrade_threshold_ms) else HealthStatus.HEALTHY
            return HealthCheckResult(status=status, response_time_ms=elapsed)
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"HTTP dep failed: {repr(e)}")
