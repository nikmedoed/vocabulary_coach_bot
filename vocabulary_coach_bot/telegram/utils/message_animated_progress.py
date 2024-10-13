import asyncio
import random
import typing

from aiogram import types
from aiogram.utils.exceptions import MessageError

from telegram.texts import Text


async def watch_fire_indicator(message: types.Message,
                               text: str,
                               markup: typing.Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup] = None,
                               indicators: typing.Union[str, typing.List[str]] = Text.misc.eyes.value):
    try:
        i = 1
        while i < 6:
            await message.edit_text(
                text + f'\n\n{" ".join(random.choices(indicators, k=i))}',
                reply_markup=markup)
            i += 1
            await asyncio.sleep(2)
        try:
            await message.delete()
        except:
            pass
    except MessageError:
        pass
