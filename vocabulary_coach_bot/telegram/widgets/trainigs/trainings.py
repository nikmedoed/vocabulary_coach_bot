import asyncio
import typing

from aiogram import F, Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from telegram.filters import IsUserFilter
from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.message_animated_progress import watch_fire_indicator
from telegram.widgets.trainigs import trainings_answers, trainings_reminder
from telegram.widgets.trainigs.trainings_common import training_result_to_sheet, training_send_new_question
from telegram.widgets.trainigs.trainings_generate import (
    training_button_stop,
    generate_question_message,
    Trainings,
    TrainingsCallbackData,
    TrainingActionCallbackData,
    training_select_message_generator,
    training_select_keyboard,
)


# TODO обработка ошибок, т.к. если слов меньше 16, нет смысла в режиме выбора и таблица сообщает о невозможности режима
async def training_select_message(message: typing.Union[types.Message, types.CallbackQuery],
                                  state: typing.Optional[FSMContext] = None):
    if isinstance(message, types.CallbackQuery):
        await message.answer()
        message = message.message
    text, markup = await training_select_message_generator(state)
    await message.answer(text, reply_markup=markup)


async def training_show_hint(query: types.CallbackQuery, storage: RedisStorage2ext):
    user_id = query.from_user.id
    current_state = await storage.get_state(user=user_id)
    train_type = current_state and current_state.split(":")[-1]
    question = (await storage.get_bucket(user=user_id)).get('question')
    await query.message.edit_text(**generate_question_message(question, train_type, hint=True))
    await query.answer()


async def training_next_message(query: types.CallbackQuery, storage: RedisStorage2ext):
    bucket = await storage.get_bucket(user=query.from_user.id)
    question = bucket.get('question') if bucket else None
    if not question:
        await query.answer("Текущий вопрос не найден, отправляю новый")
        await training_send_new_question(query.from_user.id, query.bot)
        return

    hint_text = question.get('hint') or ""
    text = (
        Text.trainings.answer.value.format(**question) +
        (f"\n\n{Text.trainings.hint.value.format(hint_text)}" if hint_text else "")
    )
    await query.answer()
    await asyncio.gather(
        training_send_new_question(query.from_user.id, query.bot),
        watch_fire_indicator(query.message, text),
        training_result_to_sheet(query.from_user.id, storage, bucket),
    )


async def training_set_and_start(query: types.CallbackQuery, callback_data: TrainingsCallbackData, state: FSMContext):
    tran_type = callback_data.type
    await state.set_state(getattr(Trainings, tran_type))
    await query.answer(f"'{Text.trainings[tran_type].value}'{Text.trainings.start_message.value}")
    await query.message.edit_reply_markup(reply_markup=training_select_keyboard(tran_type))
    await training_send_new_question(query.from_user.id, query.bot)


async def training_stop_message(message: typing.Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.CallbackQuery):
        await message.answer()
        message = message.message
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[training_button_stop()]])
    reply = await message.answer(
        Text.trainings.stop_message.value.format("👁‍🗨"),
        reply_markup=markup)
    if isinstance(message, types.Message):
        await message.delete()
    await watch_fire_indicator(reply, Text.trainings.stop_message.value, markup)


async def training_stop_callback(query: types.CallbackQuery, storage: RedisStorage2ext, state: FSMContext):
    await query.answer("")
    await state.clear()
    await training_result_to_sheet(query.from_user.id, storage)
    # TODO статистика тренировки (длительность, точность, сколько вопросов, баллы) + вывод + очистка

    await query.message.delete()
    await training_select_message(query.message, state)


def register(router: Router):
    trainings_answers.register(router)

    router.callback_query.register(training_show_hint, TrainingActionCallbackData.filter(F.action == "hint"),
                                   StateFilter(Trainings))

    router.callback_query.register(training_next_message, TrainingActionCallbackData.filter(F.action == "next"),
                                   StateFilter(Trainings))

    router.message.register(training_select_message, CommandStart(), StateFilter(None), IsUserFilter(is_user=True))

    router.callback_query.register(training_stop_callback, TrainingActionCallbackData.filter(F.action == "stop"),
                                   StateFilter(Trainings))

    trainings_reminder.register(router)
    router.callback_query.register(training_set_and_start, TrainingsCallbackData.filter(), StateFilter(None))

    router.message.register(training_stop_message, StateFilter(Trainings))
    router.callback_query.register(training_stop_message, StateFilter(Trainings))
