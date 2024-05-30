# Dynamic Semaphore and Rate Limiter

This Python module provides implementations of a dynamic semaphore and a rate limiter.

## Dynamic Semaphore

The `DynamicSemaphore` class allows for asynchronous acquisition and release of permits based on a dynamically changing limit. It is especially useful in scenarios where the rate of acquiring permits needs to adapt over time.

### Initialization Parameters

- `value`: Start value of the semaphore (default is 0).
- `limit`: Start limit of the semaphore (default is 1).
- `step_time`: Time interval (in seconds) to increase the limit (default is 10).
- `step_safe`: Recovery step for the limit (default is 1).
- `start_from`: Monotonic time from which to start (default is the current monotonic time).

### Methods

- `limit`: Calculates the current limit based on elapsed time and step parameters.
- `acquire()`: Asynchronously acquires a permit. Returns `True` if successfully acquired.
- `release()`: Releases a permit.
- `locked()`: Checks if the semaphore is locked based on the current limit.
- `__aenter__()` and `__aexit__()`: Allow usage of `async with` to acquire and release permits asynchronously.

## Rate Limiter

The `RateLimiter` class extends the functionality of `DynamicSemaphore` to include backpressure handling.

### Method

- `backpressure_handler(retry_interval)`: Asynchronously adjusts the `step_safe_base` and `start_from` parameters to handle backpressure based on the retry interval.

## Usage

```python
import asyncio
from rate_limiter import RateLimiter

async def main():
    async with RateLimiter() as limiter:
        # Your asynchronous code here
        pass

asyncio.run(main())
```