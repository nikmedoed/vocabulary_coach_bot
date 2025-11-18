import asyncio
import datetime
import logging

from aiogram import Bot, Router, types, F
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData

from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys, TRAINING_FREQUENCY_OPTIONS
from telegram.widgets.trainigs.trainings_generate import (
    training_select_message_generator,
    training_button_stop,
    Trainings,
)


class TrainingReminderCallbackData(CallbackData, prefix="TrainRemindOK"):
    action: str


async def reminder_trainings(bot: Bot):
    storage: RedisStorage2ext = bot.storage
    users = await storage.get_all_users(StorageKeys.TRAINING_FREQUENCY)
    for user in users:
        try:
            freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=user)
            pdate = await storage.get_key(StorageKeys.PREVIOUS_MESSAGE_DATE, user=user)

            if freq and int(freq) > 0 and (not pdate or int(pdate) < (
                    datetime.datetime.now() - datetime.timedelta(hours=int(freq))).timestamp()):
                state = await storage.get_state(user=user)
                if not state:
                    text, markup = await training_select_message_generator()
                    text = f'{Text.trainings.remind_start}{text}'
                else:
                    state = state.split(':')[-1]
                    text = Text.trainings.remind_continue.value.format(Text.trainings[state])
                    markup = types.InlineKeyboardMarkup(inline_keyboard=[[
                        training_button_stop(),
                        types.InlineKeyboardButton(
                            text=Text.trainings.remind_read.value,
                            callback_data=TrainingReminderCallbackData(action="ok").pack()
                        ),
                    ]])
                rows = [
                    [types.InlineKeyboardButton(
                        text=Text.trainings.remind_pause.value.format(i),
                        callback_data=TrainingReminderCallbackData(action=str(i)).pack()
                    )] for i in TRAINING_FREQUENCY_OPTIONS
                ]
                if markup.inline_keyboard:
                    markup.inline_keyboard.extend(rows)
                else:
                    markup = types.InlineKeyboardMarkup(inline_keyboard=rows)
                message = await bot.send_message(user, text, reply_markup=markup)
                await storage.set_key(
                    StorageKeys.PREVIOUS_MESSAGE_DATE,
                    round(datetime.datetime.now().timestamp()),
                    user=user)
                previous_message_id = await storage.get_key(StorageKeys.PREVIOUS_REMINDER_ID, user=user)
                if previous_message_id:
                    try:
                        await bot.delete_message(user, previous_message_id)
                    except:
                        pass
                await storage.set_key(
                    StorageKeys.PREVIOUS_REMINDER_ID,
                    message.message_id,
                    user=user)
        except TelegramForbiddenError:
            await storage.set_key(StorageKeys.TRAINING_FREQUENCY, None, user=user)
            await storage.set_key(StorageKeys.PREVIOUS_MESSAGE_DATE, None, user=user)
        except Exception as e:
            logging.error(f"Trainings reminder error - {e.__class__}: {e.with_traceback()}")
            await asyncio.sleep(1)
        await asyncio.sleep(0.1)


async def answer_training_continue(query: types.CallbackQuery):
    await query.answer()
    await query.message.delete()


async def answer_training_reminder_pause(query: types.CallbackQuery, storage: RedisStorage2ext,
                                         callback_data: TrainingReminderCallbackData):
    pause = callback_data.action
    user = query.from_user.id
    await query.answer(Text.trainings.remind_pause_ok.value.format(pause))
    try:
        await query.message.delete()
    except:
        pass
    await storage.set_key(StorageKeys.PREVIOUS_REMINDER_ID, None, user=user)
    freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=user)
    time = round((datetime.datetime.now() + datetime.timedelta(hours=int(pause) - int(freq))).timestamp())
    await storage.set_key(StorageKeys.PREVIOUS_MESSAGE_DATE, time, user=user)


def register(router: Router):
    router.callback_query.register(answer_training_continue, TrainingReminderCallbackData.filter(F.action == "ok"),
                                   StateFilter(Trainings))
    router.callback_query.register(answer_training_reminder_pause, TrainingReminderCallbackData.filter())
