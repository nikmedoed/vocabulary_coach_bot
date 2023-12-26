from aiogram import types, Dispatcher

from telegram.texts import Text
from .settings import sheet_url_show_message
from ..utils.aiogram_redis_ext import RedisStorage2ext


async def start_dialogue(message: types.Message, storage: RedisStorage2ext):
    await message.answer(Text.start.start)
    await sheet_url_show_message(message, storage)


def register(dispatcher: Dispatcher):
    dispatcher.register_message_handler(start_dialogue, is_user=False)
