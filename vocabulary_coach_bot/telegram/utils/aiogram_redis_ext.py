import json
import typing
from collections import defaultdict

from aiogram.fsm.storage.base import DefaultKeyBuilder, StorageKey, StateType
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

try:
    from redis.asyncio.connection import HiredisParser
except ImportError:  # pragma: no cover - hiredis not installed
    HiredisParser = None  # type: ignore[assignment]


class RedisStorage2ext(RedisStorage):

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: typing.Optional[int] = None,
        password: typing.Optional[str] = None,
        prefix: str = "fsm",
        state_ttl: typing.Optional[int] = None,
        data_ttl: typing.Optional[int] = None,
    ):
        pool_kwargs = dict(host=host, port=port, db=db, password=password)
        if HiredisParser is not None:
            pool_kwargs["parser_class"] = HiredisParser
        pool = ConnectionPool(**pool_kwargs)
        redis_client = Redis(connection_pool=pool)
        key_builder = DefaultKeyBuilder(prefix=prefix)
        super().__init__(
            redis=redis_client,
            key_builder=key_builder,
            state_ttl=state_ttl,
            data_ttl=data_ttl,
        )
        self._bot_id = 0
        self.custom_prefix = prefix

    def set_bot_id(self, bot_id: int):
        self._bot_id = bot_id

    # region helpers
    async def _call(self, method, key, *, chat=None, user=None, **kwargs):
        storage_key = self._storage_key(key, chat=chat, user=user)
        return await method(storage_key, **kwargs)

    def _normalize_address(
        self,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
    ) -> tuple[typing.Union[str, int], typing.Union[str, int]]:
        if chat is None and user is None:
            raise ValueError("chat or user must be provided")
        if chat is None:
            chat = user
        if user is None:
            user = chat
        return chat, user

    def _storage_key(
        self,
        key: typing.Optional[StorageKey] = None,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
    ) -> StorageKey:
        if isinstance(key, StorageKey):
            return key
        chat_id, user_id = self._normalize_address(chat, user)
        return StorageKey(
            bot_id=self._bot_id,
            chat_id=int(chat_id),
            user_id=int(user_id),
            thread_id=None,
        )

    def _custom_key(
        self,
        key: str,
        *,
        chat: typing.Union[str, int, None],
        user: typing.Union[str, int, None],
    ) -> str:
        chat_id, user_id = self._normalize_address(chat, user)
        return f"{self.custom_prefix}:{chat_id}:{user_id}:{key}"

    # endregion

    # region compatibility wrappers around base storage API
    async def set_state(
        self,
        key: typing.Union[StorageKey, None] = None,
        state: StateType = None,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
    ):
        return await self._call(super().set_state, key, chat=chat, user=user, state=state)

    async def get_state(
        self,
        key: typing.Union[StorageKey, None] = None,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
    ) -> typing.Optional[str]:
        return await self._call(super().get_state, key, chat=chat, user=user)

    async def get_data(
        self,
        key: typing.Union[StorageKey, None] = None,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
    ) -> dict:
        return await self._call(super().get_data, key, chat=chat, user=user)

    async def set_data(
        self,
        key: typing.Union[StorageKey, None] = None,
        data: typing.Mapping[str, typing.Any] = None,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
    ):
        if data is None:
            data = {}
        return await self._call(super().set_data, key, chat=chat, user=user, data=data)

    async def get_bucket(self, *, chat: typing.Union[str, int, None] = None,
                         user: typing.Union[str, int, None] = None) -> dict:
        return await self.get_data(chat=chat, user=user)

    async def update_bucket(self, *, chat: typing.Union[str, int, None] = None,
                            user: typing.Union[str, int, None] = None, **kwargs):
        data = await self.get_bucket(chat=chat, user=user)
        data.update(kwargs)
        await self.set_data(chat=chat, user=user, data=data)

    # endregion

    # region custom key/value helpers (not tied to FSM)
    async def get_key(
        self,
        key: typing.Union[str, int],
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        default: typing.Optional[typing.Any] = None,
    ) -> typing.Optional[typing.Union[str, int, None]]:
        redis_key = self._custom_key(str(key), chat=chat, user=user)
        raw_result = await self.redis.get(redis_key)
        if raw_result is None:
            return default
        try:
            return json.loads(raw_result)
        except Exception:
            return raw_result

    async def set_key(
        self,
        key: typing.Union[str, int],
        value: typing.Any,
        *,
        chat: typing.Union[str, int, None] = None,
        user: typing.Union[str, int, None] = None,
        expire: typing.Optional[int] = None,
    ):
        redis_key = self._custom_key(str(key), chat=chat, user=user)
        if value is None or value == "":
            await self.redis.delete(redis_key)
            return
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.redis.set(redis_key, str(value), ex=expire)

    async def get_all_users_keys(self, key: typing.Union[str, int] = "*"):
        redis_key = self._custom_key(str(key), chat="*", user="*")
        return await self.redis.keys(redis_key)

    async def get_all_users(self, key: typing.Union[str, int] = "*"):
        keys = await self.get_all_users_keys(key)
        return set(k.decode().split(":")[3] if isinstance(k, bytes) else k.split(":")[3] for k in keys)

    async def get_all_users_values(self, key: typing.Union[str, int] = "*") -> dict:
        keys = await self.get_all_users_keys(key)
        user_values = defaultdict(dict)
        for key_name in keys:
            if isinstance(key_name, bytes):
                key_name = key_name.decode()
            user, value_key = key_name.split(":")[-2:]
            value = await self.redis.get(key_name)
            user_values[user][value_key] = value.decode() if isinstance(value, bytes) else value
        return user_values

    async def get_user_keys(self, user: typing.Union[str, int, None],
                            chat: typing.Union[str, int, None] = "*") -> list:
        redis_key = self._custom_key("*", chat=chat, user=user)
        return await self.redis.keys(redis_key)

    async def delete_user_data(self, user: typing.Union[str, int],
                               chat: typing.Union[str, int, None] = "*") -> None:
        user_keys = await self.get_user_keys(user, chat)
        if user_keys:
            await self.redis.delete(*user_keys)

    async def delete_user_personal_data(self, user: typing.Union[str, int]) -> None:
        user_keys = await self.get_user_keys(user, user)
        if user_keys:
            await self.redis.delete(*user_keys)

    # endregion
