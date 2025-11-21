from __future__ import annotations

import sys
from typing import Iterator

from redis import Redis

from vocabulary_coach_bot.telegram.utils.config_types import readconfig


def iter_keys(client: Redis, pattern: str, batch_size: int = 500) -> Iterator[str]:
    cursor = 0
    while True:
        cursor, keys = client.scan(cursor=cursor, match=pattern, count=batch_size)
        for key in keys:
            yield key.decode() if isinstance(key, bytes) else key
        if cursor == 0:
            break


def migrate(client: Redis, prefix: str, batch_size: int = 500) -> dict:
    pattern = f"{prefix}:*:*:data"
    stats = {"processed": 0, "migrated": 0, "missing": 0}

    for key in iter_keys(client, pattern, batch_size):
        stats["processed"] += 1
        target_key = f"{key.rsplit(':', 1)[0]}:bucket"
        value = client.get(key)
        if value is None:
            stats["missing"] += 1
            continue
        ttl = client.ttl(key)
        client.set(target_key, value)
        if ttl and ttl > 0:
            client.expire(target_key, ttl)
        client.delete(key)
        stats["migrated"] += 1
        print(f"{key} -> {target_key}")
    return stats


def main() -> int:
    config = readconfig()
    redis_conf = config.redis_conf
    if redis_conf is None:
        raise SystemExit("Redis config is missing in global_settings.ini")
    client = Redis(
        host=redis_conf.host,
        port=redis_conf.port,
        db=redis_conf.db or 0,
        password=redis_conf.password,
    )
    stats = migrate(client, redis_conf.prefix)
    print(
        "Done. Processed={processed} migrated={migrated} missing={missing}".format(
            **stats
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
