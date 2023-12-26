import typing

from aiogram import types, filters, Dispatcher
from aiogram.dispatcher import FSMContext

from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.message_animated_progress import watch_fire_indicator
from telegram.widgets.trainigs import trainings_answers, trainings_reminder
from telegram.widgets.trainigs.trainings_common import training_result_to_sheet, training_send_new_question
from telegram.widgets.trainigs.trainings_generate import (
    training_button_stop, generate_question_message, Trainings,
    trainings_cb, training_action_button, training_select_message_generator, training_select_keyboard
)
import asyncio


# TODO обработка ошибок, т.к. если слов меньше 16, нет смысла в режиме выбора и таблица сообщает о невозможности режима
async def training_select_message(message: typing.Union[types.Message, types.CallbackQuery],
                                  state: FSMContext = "", **extra):
    if type(message) is types.CallbackQuery:
        await message.answer()
        message = message.message
    text, markup = await training_select_message_generator(state)
    await message.answer(text, reply_markup=markup)


async def training_show_hint(query: types.CallbackQuery, storage: RedisStorage2ext):
    user_id = query.from_user.id
    train_type = (await storage.get_state(user=user_id)).split(":")[-1]
    question = (await storage.get_bucket(user=user_id)).get('question')
    await query.message.edit_text(**generate_question_message(question, train_type, hint=True))
    await query.answer()


async def training_next_message(query: types.CallbackQuery, storage: RedisStorage2ext):
    bucket = await storage.get_bucket(user=query.from_user.id)
    question = bucket.get('question')
    text = (Text.trainings.answer.value.format(**question) +
            (f"\n\n{Text.trainings.hint.value.format(question['hint'])}" if question['hint'] else ""))
    await asyncio.gather(
        query.answer(),
        training_send_new_question(query.from_user.id, query.bot),
        watch_fire_indicator(query.message, text),
        training_result_to_sheet(query.from_user.id, storage, bucket),
    )


async def training_set_and_start(query: types.CallbackQuery, callback_data: dict):
    tran_type = callback_data["type"]
    await getattr(Trainings, tran_type).set()
    await query.answer(f"'{Text.trainings[tran_type].value}'{Text.trainings.start_message.value}")
    await query.message.edit_reply_markup(training_select_keyboard(tran_type))
    await training_send_new_question(query.from_user.id, query.bot)


async def training_stop_message(message: typing.Union[types.Message, types.CallbackQuery]):
    if type(message) is types.CallbackQuery:
        await message.answer()
        message = message.message
    markup = types.InlineKeyboardMarkup().add(training_button_stop())
    reply = await message.answer(
        Text.trainings.stop_message.value.format("👁‍🗨"),
        reply_markup=markup)
    if type(message) is types.Message:
        await message.delete()
    await watch_fire_indicator(reply, Text.trainings.stop_message.value, markup)


async def training_stop_callback(query: types.CallbackQuery, storage: RedisStorage2ext, state: FSMContext):
    await query.answer("")
    await state.finish()
    await training_result_to_sheet(query.from_user.id, storage)
    # TODO статистика тренировки (длительность, точность, сколько вопросов, баллы) + вывод + очистка

    await query.message.delete()
    await training_select_message(query.message, state)


def register(dispatcher: Dispatcher):
    # dispatcher.register_message_handler(training_select_message, is_user=True, state=None)

    trainings_answers.register(dispatcher)

    dispatcher.register_callback_query_handler(training_show_hint,
                                               training_action_button.filter(action="hint"),
                                               state=Trainings)

    dispatcher.register_callback_query_handler(training_next_message,
                                               training_action_button.filter(action="next"),
                                               state=Trainings)

    dispatcher.register_message_handler(training_select_message, filters.CommandStart(), state=None, is_user=True)

    dispatcher.register_callback_query_handler(training_stop_callback,
                                               training_action_button.filter(action="stop"),
                                               state=Trainings)

    trainings_reminder.register(dispatcher)
    dispatcher.register_callback_query_handler(training_set_and_start, trainings_cb.filter(), state=None)

    dispatcher.register_message_handler(training_stop_message, state=Trainings)
    dispatcher.register_callback_query_handler(training_stop_message, state=Trainings)
