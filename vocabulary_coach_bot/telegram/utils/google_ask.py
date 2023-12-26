import asyncio
import logging

import aiohttp


async def google_ask(data: dict, gsapi: str) -> dict:
    errors = 0
    while 1:
        errors += 1
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(gsapi, json=data) as resp:
                    answ = await resp.json()
                    if answ.get("error"):
                        logging.error(f"{answ.get('error')} {answ.get('data')}")
                    else:
                        return answ['ok']
        except:
            if errors > 5:
                return {"error": "google doesn't answer"}
            await asyncio.sleep(2)
