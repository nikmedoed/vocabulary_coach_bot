import re

from aiogram import types, filters, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys
from telegram.utils.spreadsheet_connector import SpreadSheetConnector
from telegram.widgets.trainigs.trainings import training_select_message


def settings_generate_markup():
    return types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, selective=True).add(*[
        types.KeyboardButton(text=butt.value) for butt in Text.settings if butt.name.startswith("button_")
    ])


async def show_settings_buttons(message: types.Message):
    await message.answer(Text.settings.welcome, reply_markup=settings_generate_markup())


async def hide_settings_buttons(message: types.Message):
    await message.delete()
    mes = await message.answer("Скрываем", reply_markup=types.ReplyKeyboardRemove())
    await mes.delete()
    await training_select_message(message)


class SetUrlMessage(StatesGroup):
    sheet_url = State()


async def sheet_url_show_message(message: types.Message, storage: RedisStorage2ext):
    url = await storage.get_key(StorageKeys.SHEET_URL, user=message.from_user.id)
    await message.answer(
        Text.settings.sheet_url_message.value + (f"\n\n{Text.settings.sheet_url_message_cancel}" if url else ""),
        reply_markup=types.ReplyKeyboardRemove())
    await SetUrlMessage.sheet_url.set()


async def sheet_url_check(message: types.Message, state: FSMContext, storage: RedisStorage2ext):
    result = re.match(r"https://script.google.com/macros/s/[\S]*/exec", message.text)
    if result:
        try:
            url = result.group(0)
            version = await SpreadSheetConnector.check_version(url)
            await storage.set_key(StorageKeys.SHEET_URL, value=url, user=message.from_user.id)
            await state.finish()
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
    await state.finish()
    await show_settings_buttons(message)


frequency_cb = CallbackData('frequency', 'hours')


async def frequency_show_message(message: types.Message, storage: RedisStorage2ext):
    markup = await frequency_generate_keyboard(message.from_user.id, storage)
    await message.answer(
        Text.settings.frequency_message,
        reply_markup=markup
    )


async def frequency_generate_keyboard(user_id, storage: RedisStorage2ext):
    freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=user_id)
    freq = freq and int(freq)
    markup = types.InlineKeyboardMarkup().row(*[types.InlineKeyboardButton(
        f"{'✅ ' if fr == freq else ''}{fr}",
        callback_data=frequency_cb.new(hours=fr)
    ) for fr in [12, 24, 48, 72]])
    markup.add(types.InlineKeyboardButton(
        f"{'✅ ' if not freq else ''}{Text.settings.frequency_no}",
        callback_data=frequency_cb.new(hours=0)
    ))
    return markup


async def frequency_set(query: types.CallbackQuery, storage: RedisStorage2ext, callback_data: dict, **extra_data):
    freq = callback_data['hours']
    old_freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=query.from_user.id)
    await storage.set_key(StorageKeys.TRAINING_FREQUENCY, value=freq, user=query.from_user.id)
    if (old_freq or '0') != freq:
        await query.message.edit_reply_markup(await frequency_generate_keyboard(query.from_user.id, storage))
    await query.answer(Text.settings.frequency_set.value.format(freq) if int(freq) else Text.settings.frequency_set_no)
    if not old_freq:
        await training_select_message(query.message, **extra_data)


def register(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(frequency_set, frequency_cb.filter())
    dispatcher.register_message_handler(frequency_show_message,
                                        filters.Text(contains=Text.settings.button_frequency.value))

    dispatcher.register_message_handler(sheet_url_cancel, commands=['cancel'], state=SetUrlMessage.sheet_url)
    dispatcher.register_message_handler(sheet_url_check, state=SetUrlMessage.sheet_url)
    dispatcher.register_message_handler(sheet_url_show_message, filters.Text(contains=Text.settings.button_sheet.value))

    dispatcher.register_message_handler(show_settings_buttons, filters.CommandSettings(), is_user=True)
    dispatcher.register_message_handler(hide_settings_buttons, filters.Text(contains=Text.settings.button_close.value))
