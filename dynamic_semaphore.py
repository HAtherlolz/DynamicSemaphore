import time
import asyncio

from typing import NoReturn


class DynamicSemaphore:
    def __init__(
            self,
            value: int = 0,
            limit: int = 1,
            step_time: int = 10,
            step_safe: int = 1,
            start_from: float = time.monotonic()
    ) -> NoReturn:
        """
       :param value: - start value
       :param limit: - start limit
       :param step_time: - time interval to increase the limit
       :param step_safe: - recovery step
       :param start_from: - monotonic time for start
       """
        self._value = value
        self._limit = limit
        self._step_time = step_time
        self._step_safe_base = step_safe
        self._start_from = start_from

    @property
    def limit(self) -> int:

        current_time = time.monotonic()
        if current_time < self._start_from:
            return 1
        elapsed = current_time - self._start_from
        steps = int(elapsed // self._step_time)
        current_limit = self._step_safe_base + steps
        return current_limit

    async def acquire(self) -> bool:
        while True:
            if not self.locked:
                self._value += 1
                return True
            await asyncio.sleep(1)

    def release(self) -> NoReturn:
        self._value -= 1

    @property
    def locked(self) -> bool:
        return self._value >= self.limit

    def __enter__(self):
        raise RuntimeError("Use 'async with' to acquire DynamicSemaphore asynchronously")

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise RuntimeError("Use 'async with' to release DynamicSemaphore asynchronously")

    async def __aenter__(self) -> NoReturn:
        await self.acquire()

    async def __aexit__(self, exc_type, exc, tb) -> NoReturn:
        self.release()




