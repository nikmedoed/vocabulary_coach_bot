from aiogram import Router, types

from telegram.filters import IsUserFilter
from telegram.texts import Text
from .settings import sheet_url_show_message
from ..utils.aiogram_redis_ext import RedisStorage2ext


async def start_dialogue(message: types.Message, storage: RedisStorage2ext, state):
    await message.answer(Text.start.start)
    await sheet_url_show_message(message, storage, state)


def register(router: Router):
    router.message.register(start_dialogue, IsUserFilter(is_user=False))
