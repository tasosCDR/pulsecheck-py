from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class HealthStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


@dataclass
class HealthCheckResult:
    status: HealthStatus
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OverallHealthResponse:
    status: HealthStatus
    timestamp: datetime
    environment: str
    checks: Dict[str, HealthCheckResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "environment": self.environment,
            "checks": {
                name: {
                    "status": res.status.value,
                    **({"response_time_ms": res.response_time_ms} if res.response_time_ms is not None else {}),
                    **({"error": res.error} if res.error else {}),
                    **({"meta": res.meta} if res.meta else {}),
                }
                for name, res in self.checks.items()
            },
        }
