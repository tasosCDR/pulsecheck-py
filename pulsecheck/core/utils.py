from __future__ import annotations

import asyncio
import time
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


def now_ms(start_perf: float) -> float:
    return (time.perf_counter() - start_perf) * 1000.0


async def with_timeout(awaitable: Awaitable[T], timeout_s: float) -> T:
    return await asyncio.wait_for(awaitable, timeout=timeout_s)


async def to_thread(fn: Callable[[], T]) -> T:
    return await asyncio.to_thread(fn)
