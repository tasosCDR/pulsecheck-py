from __future__ import annotations

import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from ..models import HealthCheckResult, HealthStatus
from ..utils import now_ms, with_timeout
from .base import CheckConfig, HealthCheck


class SQLAlchemyAsyncCheck(HealthCheck):
    def __init__(self, engine: AsyncEngine, *, name: str = "database", timeout_s: float = 2.0, degrade_threshold_ms: float = 500.0) -> None:
        super().__init__(CheckConfig(name=name, readiness=True, timeout_s=timeout_s, degrade_threshold_ms=degrade_threshold_ms))
        self._engine = engine

    async def check(self) -> HealthCheckResult:
        start = time.perf_counter()

        async def _run() -> None:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

        try:
            await with_timeout(_run(), self.config.timeout_s)
            elapsed = now_ms(start)
            status = HealthStatus.DEGRADED if (self.config.degrade_threshold_ms and elapsed > self.config.degrade_threshold_ms) else HealthStatus.HEALTHY
            return HealthCheckResult(status=status, response_time_ms=elapsed)
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"Database failed: {repr(e)}")
