from __future__ import annotations

import time
from kombu import Connection, Exchange  # type: ignore

from ..models import HealthCheckResult, HealthStatus
from ..utils import now_ms, to_thread, with_timeout
from .base import CheckConfig, HealthCheck


class RabbitMQKombuCheck(HealthCheck):
    def __init__(
        self,
        amqp_url: str,
        *,
        name: str = "rabbitmq",
        timeout_s: float = 3.0,
        degrade_threshold_ms: float = 1000.0,
        exchange_name: str | None = None,
        exchange_type: str = "direct",
    ) -> None:
        super().__init__(CheckConfig(name=name, readiness=True, timeout_s=timeout_s, degrade_threshold_ms=degrade_threshold_ms))
        self._url = amqp_url
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type

    async def check(self) -> HealthCheckResult:
        start = time.perf_counter()

        def _sync() -> None:
            with Connection(self._url, connect_timeout=self.config.timeout_s) as conn:
                conn.ensure_connection(max_retries=1)
                if self._exchange_name:
                    exchange = Exchange(name=self._exchange_name, type=self._exchange_type, passive=True)
                    with conn.channel() as channel:
                        exchange(channel).declare()

        try:
            await with_timeout(to_thread(_sync), self.config.timeout_s)
            elapsed = now_ms(start)
            status = HealthStatus.DEGRADED if (self.config.degrade_threshold_ms and elapsed > self.config.degrade_threshold_ms) else HealthStatus.HEALTHY
            return HealthCheckResult(status=status, response_time_ms=elapsed)
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, error=f"RabbitMQ failed: {repr(e)}")
