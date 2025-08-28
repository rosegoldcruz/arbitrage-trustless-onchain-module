import asyncio
import contextlib
import logging

log = logging.getLogger("atom.safe")

class CircuitBreaker:
    def __init__(self, fail_max: int = 5, reset_after: float = 30.0):
        self.fail_max = fail_max
        self.reset_after = reset_after
        self.fail_count = 0
        self.open_until = 0.0

    def can_run(self, now: float) -> bool:
        return now >= self.open_until

    def record(self, ok: bool, now: float) -> None:
        if ok:
            self.fail_count = 0
        else:
            self.fail_count += 1
            if self.fail_count >= self.fail_max:
                self.open_until = now + self.reset_after
                log.error("Circuit opened for %ss", self.reset_after)

async def guard(coro, *, timeout: float = 10.0, retries: int = 3, backoff: float = 0.5, breaker: CircuitBreaker | None = None):
    for attempt in range(retries):
        if breaker and not breaker.can_run(asyncio.get_event_loop().time()):
            raise RuntimeError("Circuit open")
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            if breaker:
                breaker.record(True, asyncio.get_event_loop().time())
            return result
        except Exception as e:
            if breaker:
                breaker.record(False, asyncio.get_event_loop().time())
            if attempt == retries - 1:
                raise
            await asyncio.sleep(backoff * (2 ** attempt))

@contextlib.asynccontextmanager
async def cancellation_shield():
    try:
        yield
    except asyncio.CancelledError:
        raise 