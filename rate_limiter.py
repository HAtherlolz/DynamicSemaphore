import time

from typing import NoReturn

from dynamic_semaphore import DynamicSemaphore


class RateLimiter(DynamicSemaphore):
    async def backpressure_handler(self, retry_interval) -> NoReturn:
        current_time = time.monotonic()
        if current_time > self._start_from:
            self._step_safe_base = max(self._value - 1, 1)
            new_start_from = current_time + retry_interval
            self._start_from = max(self._start_from, new_start_from)
