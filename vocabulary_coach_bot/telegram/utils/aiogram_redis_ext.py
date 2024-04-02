import typing

from aiogram.contrib.fsm_storage.redis import RedisStorage2
from collections import defaultdict


class RedisStorage2ext(RedisStorage2):
    async def get_key(self, key, *, chat: typing.Union[str, int, None] = None,
                      user: typing.Union[str, int, None] = None,
                      default: typing.Optional[dict] = None) -> typing.Optional[typing.Union[str, int, None]]:
        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, str(key))
        redis = self._redis
        raw_result = await redis.get(key)
        return raw_result or default

    async def set_key(self, key, value, *, chat: typing.Union[str, int, None] = None,
                      user: typing.Union[str, int, None] = None):
        chat, user = self.check_address(chat=chat, user=user)
        key = self.generate_key(chat, user, str(key))
        redis = self._redis
        if value:
            await redis.set(key, str(value), ex=self._bucket_ttl)
        else:
            await redis.delete(key)

    async def get_all_users_keys(self, key="*"):
        key = self.generate_key("*", "*", str(key))
        redis = self._redis
        return await redis.keys(key)

    async def get_all_users(self, key="*"):
        keys = await self.get_all_users_keys(key)
        return set([k.split(":")[2] for k in keys])

    async def get_all_users_values(self, key="*") -> dict:
        keys = await self.get_all_users_keys(key)
        user_values = defaultdict(dict)
        redis = self._redis
        for key in keys:
            user, value_key = key.split(":")[-2:]
            value = await redis.get(key)
            user_values[user][value_key] = value
        return user_values

    async def get_user_keys(self, user: typing.Union[str, int, None],
                            chat: typing.Union[str, int, None] = "*") -> list:
        """
        Возвращает список всех ключей для конкретного пользователя
        """
        key = self.generate_key(chat, user, "*")
        redis = self._redis
        return await redis.keys(key)

    async def delete_user_data(self, user: typing.Union[str, int], chat: typing.Union[str, int, None] = "*") -> None:
        """
        Удаляет все ключи для конкретного пользователя
        """
        user_keys = await self.get_user_keys(user, chat)
        redis = self._redis
        if user_keys:
            await redis.delete(*user_keys)

    async def delete_user_personal_data(self, user: typing.Union[str, int]) -> None:
        """
        Удаляет все ключи в личном чате пользователя
        """
        user_keys = await self.get_user_keys(user, user)
        redis = self._redis
        if user_keys:
            await redis.delete(*user_keys)
