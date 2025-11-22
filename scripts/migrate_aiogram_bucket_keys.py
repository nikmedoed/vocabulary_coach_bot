from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import AsyncIterator

from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.connection import ConnectionPool

try:
    from redis.asyncio.connection import HiredisParser
except ImportError:  # pragma: no cover - hiredis missing locally
    HiredisParser = None  # type: ignore[assignment]

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from vocabulary_coach_bot.telegram.utils.config_types import readconfig

async def iter_keys(client: AsyncRedis, pattern: str, batch_size: int = 500) -> AsyncIterator[str]:
    cursor = 0
    while True:
        cursor, keys = await client.scan(cursor=cursor, match=pattern, count=batch_size)
        for key in keys:
            yield key.decode() if isinstance(key, bytes) else key
        if cursor == 0:
            break


async def migrate(client: AsyncRedis, prefix: str, batch_size: int = 500) -> dict:
    pattern = f"{prefix}:*:*:bucket"
    stats = {"processed": 0, "migrated": 0, "missing": 0, "skipped_existing": 0}

    async for key in iter_keys(client, pattern, batch_size):
        stats["processed"] += 1
        target_key = f"{key.rsplit(':', 1)[0]}:data"
        if await client.exists(target_key):
            stats["skipped_existing"] += 1
            continue
        value = await client.get(key)
        if value is None:
            stats["missing"] += 1
            continue
        ttl = await client.ttl(key)
        await client.set(target_key, value)
        if ttl and ttl > 0:
            await client.expire(target_key, ttl)
        await client.delete(key)
        stats["migrated"] += 1
        print(f"{key} -> {target_key}")
    return stats


async def async_main() -> int:
    config_path = ROOT_DIR / "vocabulary_coach_bot" / "global_settings.ini"
    config = readconfig(str(config_path))
    redis_conf = config.redis_conf
    if redis_conf is None:
        raise SystemExit("Redis config is missing in global_settings.ini")
    pool_kwargs = dict(
        host=redis_conf.host,
        port=redis_conf.port,
        db=redis_conf.db or 0,
        password=redis_conf.password,
    )
    if HiredisParser is not None:
        pool_kwargs["parser_class"] = HiredisParser
    pool = ConnectionPool(**pool_kwargs)
    client = AsyncRedis(connection_pool=pool)
    try:
        stats = await migrate(client, redis_conf.prefix)
    finally:
        await client.aclose()
    print(
        "Done. Processed={processed} migrated={migrated} skipped_existing={skipped_existing} "
        "missing={missing}".format(**stats)
    )
    return 0


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
