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

### Example of usage in `test.py`

- Install packages from requirements.txt
```commandline
pip install -r requirements.txt
```

- Set environments vars (env.example)
```commandline
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_VERSION=<openai-api-version>
```

- Import necessary packages
```python
import os
import re
import asyncio

from typing import NoReturn

# Third party libraries
import openai
from dotenv import load_dotenv

# Projects import
from rate_limiter import RateLimiter

```

- Load the environments vars
```python
load_dotenv()
```

- `openai_call`: This function attempts to call the OpenAI API, handling rate limiting and retries if a RateLimitError is encountered.
```python
async def openai_call(
        rate_limiter: RateLimiter,
        client: openai.AsyncOpenAI,
        model: str,
        prompt: str
) -> None:
    retries = 0
    while retries < 10:
        try:
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt},
                ],
                model=model,
            )
            llm_response = chat_completion.choices[0].message.content.strip()  # LLM RESPONSE
            if retries > 0:
                print(f"Success after retried {retries} times!")
            else:
                print(f"Success!")
            return
        except openai.RateLimitError as e:
            retries += 1
            match = re.search(r'try again in (\d+).', str(e))
            retry_after = float(match.group(1))
            print(f"Backpressure, retrying in {retry_after} seconds... (attempt {retries})")
            await rate_limiter.backpressure_handler(retry_after)
            await asyncio.sleep(retry_after)

```

- `process_names_with_api`: This function creates multiple tasks to process names with the API using a task group for concurrent execution.
```python
async def process_names_with_api(client: openai.AsyncOpenAI, model: str) -> NoReturn:
    rate_limiter = RateLimiter()

    async with asyncio.TaskGroup() as tg:
        for _ in range(100):
            prompt = "PROMPT"
            tg.create_task(worker(rate_limiter, client, model, prompt))

```

- `worker`: This function acquires the semaphore, makes the API call, and releases the semaphore.
```python
async def worker(
        rate_limiter: RateLimiter,
        client: openai.AsyncOpenAI,
        model: str,
        prompt: str
) -> NoReturn:
    try:
        await rate_limiter.acquire()  # waiting for value < limit
        await openai_call(rate_limiter, client, model, prompt)
    finally:
        rate_limiter.release()

```

- This block retrieves the API key and version from environment variables, creates an OpenAI client, and runs the process_names_with_api coroutine using the event loop.
```python
if __name__ == "__main__":
    # Gets the variables from environment
    api_key = os.getenv("OPENAI_API_KEY")
    api_version = os.getenv("OPENAI_VERSION")

    client = openai.AsyncOpenAI(api_key=api_key)

    loop = asyncio.get_event_loop()  # gets the event loop
    loop.run_until_complete(process_names_with_api(client=client, model=api_version))

```

### Summary
- This example demonstrates how to handle rate limiting and backpressure when making multiple asynchronous API calls to OpenAI using a custom RateLimiter. The RateLimiter ensures that the number of concurrent requests stays within a dynamic limit, adapting over time to the allowed rate.

### Prerequisites
- Python 3.7+
- OpenAI API key
- Required Python packages