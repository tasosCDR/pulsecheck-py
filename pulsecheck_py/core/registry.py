from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import HealthCheckResult, HealthStatus, OverallHealthResponse
from .status import combine_status


class HealthRegistry:
    def __init__(self, *, environment: str, max_concurrency: int = 10) -> None:
        self.environment = environment
        self._checks: List[object] = []
        self._max_concurrency = max_concurrency

    def register(self, check: object) -> None:
        # We keep it generic; checks must expose `config` and async `check()`.
        self._checks.append(check)

    def liveness(self) -> OverallHealthResponse:
        return OverallHealthResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(timezone.utc),
            environment=self.environment,
            checks={},
        )

    async def readiness(self) -> OverallHealthResponse:
        return await self.run(readiness_only=True)

    async def run(self, *, readiness_only: bool = False) -> OverallHealthResponse:
        checks_out: Dict[str, HealthCheckResult] = {}
        overall = HealthStatus.HEALTHY

        sem = asyncio.Semaphore(self._max_concurrency)

        async def _run_one(c) -> None:
            nonlocal overall
            async with sem:
                name = c.config.name  # type: ignore[attr-defined]
                if readiness_only and not c.config.readiness:  # type: ignore[attr-defined]
                    return
                try:
                    res: HealthCheckResult = await c.check()  # type: ignore[attr-defined]
                except Exception as e:
                    res = HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"Check crashed: {repr(e)}")
                checks_out[name] = res
                overall = combine_status(overall, res.status)

        await asyncio.gather(*[_run_one(c) for c in self._checks])

        return OverallHealthResponse(
            status=overall,
            timestamp=datetime.now(timezone.utc),
            environment=self.environment,
            checks=checks_out,
        )
