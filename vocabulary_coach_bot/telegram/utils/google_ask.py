import asyncio
import logging
import random

import aiohttp


async def google_ask(data: dict, gsapi: str, max_retries: int = 5) -> dict:
    if isinstance(gsapi, bytes):
        gsapi = gsapi.decode()

    timeout = aiohttp.ClientTimeout(total=20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for attempt in range(1, max_retries + 1):
            try:
                async with session.post(gsapi, json=data) as resp:
                    if resp.status == 429:
                        retry_after = resp.headers.get("Retry-After")
                        if retry_after:
                            try:
                                delay = float(retry_after)
                            except ValueError:
                                delay = 0
                        else:
                            delay = 0
                        delay = delay or min(2 ** attempt, 30)
                        jitter = random.uniform(0.1, 0.5)
                        wait_time = delay + jitter
                        logging.error(
                            "google_ask rate limited (%s/%s): 429, wait %.2fs",
                            attempt,
                            max_retries,
                            wait_time,
                        )
                        if attempt == max_retries:
                            return {"error": "google rate limited"}
                        await asyncio.sleep(wait_time)
                        continue

                    resp.raise_for_status()
                    answ = await resp.json()

                if answ.get("error"):
                    logging.error("%s %s", answ.get("error"), answ.get("data"))
                    return {"error": answ.get("error"), "data": answ.get("data")}

                return answ["ok"]

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.error("google_ask error (%s/%s): %s", attempt, max_retries, e)
                if attempt == max_retries:
                    return {"error": "google doesn't answer"}
                await asyncio.sleep(2)
