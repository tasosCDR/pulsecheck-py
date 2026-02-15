from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..models import HealthCheckResult


@dataclass
class CheckConfig:
    name: str
    readiness: bool = True
    timeout_s: float = 2.0
    degrade_threshold_ms: Optional[float] = None


class HealthCheck:
    """
    Implementations should be light and fast.
    - Don't run heavy DB queries.
    - Don't fetch queue depth.
    - Fail fast with short timeouts.
    """

    def __init__(self, config: CheckConfig) -> None:
        self.config = config

    async def check(self) -> HealthCheckResult:
        raise NotImplementedError
