import asyncio
import datetime

from aiogram import Bot, types, Dispatcher
from aiogram.utils.callback_data import CallbackData

from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys
from telegram.widgets.trainigs.trainings_generate import training_select_message_generator, training_button_stop, \
    Trainings

training_reminder_button = CallbackData('TrainRemindOK', 'action')


async def reminder_trainings(bot: Bot):
    storage: RedisStorage2ext = bot['storage']
    users = await storage.get_all_users(StorageKeys.TRAINING_FREQUENCY)
    for user in users:
        freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=user)
        pdate = await storage.get_key(StorageKeys.PREVIOUS_MESSAGE_DATE, user=user)

        if int(freq) > 0 and (not pdate or int(pdate) < (
                datetime.datetime.now() - datetime.timedelta(hours=int(freq))).timestamp()):
            state = await storage.get_state(user=user)
            if not state:
                text, markup = await training_select_message_generator()
                text = f'{Text.trainings.remind_start}{text}'
            else:
                state = state.split(':')[-1]
                text = Text.trainings.remind_continue.value.format(Text.trainings[state])
                markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True).add(*[
                    training_button_stop(),
                    types.InlineKeyboardButton(Text.trainings.remind_read.value,
                                               callback_data=training_reminder_button.new(action="ok"))
                ])
            markup.add(*[types.InlineKeyboardButton(
                Text.trainings.remind_pause.value.format(i),
                callback_data=training_reminder_button.new(action=i)
            ) for i in [12, 24, 48, 72]])
            await bot.send_message(user, text, reply_markup=markup)
            await storage.set_key(
                StorageKeys.PREVIOUS_MESSAGE_DATE,
                round(datetime.datetime.now().timestamp()),
                user=user)
        await asyncio.sleep(0.1)


async def answer_training_continue(query: types.CallbackQuery):
    await query.answer()
    await query.message.delete()


async def answer_training_reminder_pause(query: types.CallbackQuery, storage: RedisStorage2ext, callback_data: dict):
    pause = callback_data['action']
    await query.answer(Text.trainings.remind_pause_ok.value.format(pause))
    await query.message.delete()
    user = query.from_user.id
    freq = await storage.get_key(StorageKeys.TRAINING_FREQUENCY, user=user)
    time = round((datetime.datetime.now() + datetime.timedelta(hours=int(pause) - int(freq))).timestamp())
    await storage.set_key(StorageKeys.PREVIOUS_MESSAGE_DATE, time, user=user)


def register(dispatcher: Dispatcher):
    dispatcher.register_callback_query_handler(answer_training_continue,
                                               training_reminder_button.filter(action="ok"), state=Trainings)
    dispatcher.register_callback_query_handler(answer_training_reminder_pause,
                                               training_reminder_button.filter(), state="*")
