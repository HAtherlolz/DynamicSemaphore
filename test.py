# Standard libraries
import os
import re
import asyncio

from typing import NoReturn

# Third party libraries
import openai
from dotenv import load_dotenv

# Projects import
from rate_limiter import RateLimiter


load_dotenv()


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


async def concurrent_process(client: openai.AsyncOpenAI, model: str) -> NoReturn:
    rate_limiter = RateLimiter()

    async with asyncio.TaskGroup() as tg:
        for _ in range(100):
            prompt = "PROMPT"
            tg.create_task(worker(rate_limiter, client, model, prompt))


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


if __name__ == "__main__":
    # Gets the variables from environment
    api_key = os.getenv("OPENAI_API_KEY")
    api_version = os.getenv("OPENAI_VERSION")

    client = openai.AsyncOpenAI(api_key=api_key)

    loop = asyncio.get_event_loop()  # gets the event loop
    loop.run_until_complete(concurrent_process(client=client, model=api_version))

