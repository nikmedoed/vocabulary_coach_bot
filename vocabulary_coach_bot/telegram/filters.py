import typing

from aiogram import types
from aiogram.filters import BaseFilter

from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys


class AdminFilter(BaseFilter):
    def __init__(self, admin: typing.Optional[bool] = None):
        self.admin = admin

    async def __call__(self, message: types.Message) -> bool:
        if self.admin is None:
            return True
        return message.bot.config.admin_id == message.from_user.id


class IsUserFilter(BaseFilter):
    def __init__(self, is_user: typing.Optional[bool] = None):
        self.is_user = is_user

    async def __call__(self, message: types.Message) -> bool:
        if self.is_user is None:
            return True
        storage: RedisStorage2ext = message.bot.storage
        user_url = await storage.get_key(StorageKeys.SHEET_URL, user=message.from_user.id)
        return self.is_user == bool(user_url)
