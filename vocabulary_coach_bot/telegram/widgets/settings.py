import re

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram.filters import IsUserFilter
from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys, TRAINING_FREQUENCY_OPTIONS
from telegram.utils.database_update import DATABASE_VERSION
from telegram.utils.spreadsheet_connector import SpreadSheetConnector
from telegram.widgets.trainigs.trainings import training_select_message


def settings_generate_markup():
    buttons = [[types.KeyboardButton(text=butt.value)] for butt in Text.settings if butt.name.startswith("button_")]
    return types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, selective=True)


async def show_settings_buttons(message: types.Message):
    await message.answer(Text.settings.welcome, reply_markup=settings_generate_markup())


async def hide_settings_buttons(message: types.Message):
    await message.delete()
    mes = await message.answer("Скрываем", reply_markup=types.ReplyKeyboardRemove())
    await mes.delete()
    await training_select_message(message)


class SetUrlMessage(StatesGroup):
    sheet_url = State()


async def sheet_url_show_message(message: types.Message, storage: RedisStorage2ext, state: FSMContext):
    url = await storage.get_key(StorageKeys.SHEET_URL, user=message.from_user.id)
    await message.answer(
        Text.settings.sheet_url_message.value + (f"\n\n{Text.settings.sheet_url_message_cancel}" if url else ""),
        reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SetUrlMessage.sheet_url)


async def sheet_url_check(message: types.Message, state: FSMContext, storage: RedisStorage2ext):
    result = re.match(r"https://script.google.com/macros/s/[\S]*/exec", message.text)
    if result:
        try:
            url = result.group(0)
            version = await SpreadSheetConnector.check_version(url)
            if version != DATABASE_VERSION:
                await message.reply(Text.start.database_old_version)
                return

            await storage.set_key(StorageKeys.SHEET_URL, value=url, user=message.from_user.id)
            await state.clear()
            freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=message.from_user.id)
            await message.reply(Text.settings.sheet_url_correct,
                                reply_markup=settings_generate_markup()
                                if freq
                                else None)
            if not freq:
                await frequency_show_message(message, storage)
            return
        except:
            pass
    await message.reply(Text.settings.sheet_url_incorrect)


async def sheet_url_cancel(message: types.Message, state: FSMContext, storage: RedisStorage2ext):
    await state.clear()
    await show_settings_buttons(message)


class FrequencyCallbackData(CallbackData, prefix="frequency"):
    hours: str


async def frequency_show_message(message: types.Message, storage: RedisStorage2ext):
    markup = await frequency_generate_keyboard(message.from_user.id, storage)
    await message.answer(
        Text.settings.frequency_message,
        reply_markup=markup
    )


async def frequency_generate_keyboard(user_id, storage: RedisStorage2ext):
    freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=user_id)
    freq = freq and int(freq)
    inline_keyboard = []
    rows = [TRAINING_FREQUENCY_OPTIONS[:4], TRAINING_FREQUENCY_OPTIONS[4:]]
    for row in rows:
        inline_keyboard.append([types.InlineKeyboardButton(
            text=f"{'✅ ' if fr == freq else ''}{fr}",
            callback_data=FrequencyCallbackData(hours=str(fr)).pack()
        ) for fr in row])
    inline_keyboard.append([types.InlineKeyboardButton(
        text=f"{'✅ ' if not freq else ''}{Text.settings.frequency_no}",
        callback_data=FrequencyCallbackData(hours="0").pack()
    )])
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def frequency_set(query: types.CallbackQuery, storage: RedisStorage2ext, callback_data: FrequencyCallbackData,
                        **extra_data):
    freq = callback_data.hours
    old_freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=query.from_user.id)
    await storage.set_key(StorageKeys.TRAINING_FREQUENCY, value=freq, user=query.from_user.id)
    if (old_freq or '0') != freq:
        await query.message.edit_reply_markup(
            reply_markup=await frequency_generate_keyboard(query.from_user.id, storage)
        )
    await query.answer(
        Text.settings.frequency_set.value.format(freq) if int(freq) else Text.settings.frequency_set_no)
    if not old_freq:
        await training_select_message(query.message, **extra_data)


def register(router: Router):
    router.callback_query.register(frequency_set, FrequencyCallbackData.filter())
    router.message.register(
        frequency_show_message,
        F.text.lower().contains(Text.settings.button_frequency.value.lower()),
        IsUserFilter(is_user=True)
    )

    router.message.register(sheet_url_cancel, Command(commands=["cancel"]), SetUrlMessage.sheet_url)
    router.message.register(sheet_url_check, SetUrlMessage.sheet_url)
    router.message.register(sheet_url_show_message, F.text.lower().contains(Text.settings.button_sheet.value.lower()))

    router.message.register(show_settings_buttons, Command(commands=["settings"]), IsUserFilter(is_user=True))
    router.message.register(hide_settings_buttons, F.text.lower().contains(Text.settings.button_close.value.lower()))
