import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import StateFilter
from rapidfuzz import fuzz

from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys
from telegram.widgets.trainigs.trainings_common import training_result_to_sheet, training_send_new_question
from telegram.widgets.trainigs.trainings_generate import Trainings, TrainingSelectOneCallbackData

ANSWERS = {int(i[len('answer_score_'):]): str(k) for i, k in Text.trainings.__dict__.items() if
           i.startswith('answer_score_')}


def calculate_number_similarity(user_answer: int, correct_answer: int) -> int:
    divisor = max(10, abs(correct_answer))
    difference = abs(user_answer - correct_answer) / divisor * 100
    similarity = max(0, round(100 - difference))
    return similarity


async def answer_training_type_the_answer(message: types.Message, storage: RedisStorage2ext):
    user_id = message.from_user.id
    bot = message.bot
    bucket = await storage.get_bucket(user=user_id)
    question = bucket.get('question')

    if not question or 'word' not in question:
        await training_send_new_question(user_id, bot)
        return

    try:
        correct_answer = int(question['word'])
        user_answer = int(message.text)
        score = calculate_number_similarity(user_answer, correct_answer)
    except ValueError:
        score = fuzz.QRatio(str(question['word']).strip().lower(), str(message.text).strip().lower())

    logging.info(f"score {score}")
    text = "error"
    for i in sorted(ANSWERS.keys(), reverse=True):
        if score >= i:
            text = ANSWERS[i]
            break
    reply = await message.reply(text)

    bucket = await storage.get_bucket(user=user_id)
    answer = bucket.get('answer', {"attempts": 0, "guessed": 0})
    answer['attempts'] += 1
    post_actions = [reply.delete(), message.delete()]
    if score == 100:
        answer['guessed'] += 1
        question_id = await storage.get_key(StorageKeys.CURRENT_QUESTION_ID, user=user_id)
        post_actions.append(bot.delete_message(chat_id=user_id, message_id=question_id))
        await asyncio.gather(
            training_send_new_question(user_id, bot),
            training_result_to_sheet(user_id, storage, bucket)
        )
    else:
        await storage.update_bucket(user=user_id, answer=answer)
    await asyncio.sleep(5)
    for action in post_actions:
        try:
            await action
        except Exception:
            pass


async def answer_training_select_one(query: types.CallbackQuery, storage: RedisStorage2ext,
                                     callback_data: TrainingSelectOneCallbackData):
    user_id = query.from_user.id
    bot = query.bot
    word_index = callback_data.word_number
    if not word_index:
        await query.answer(Text.trainings.answer_select_one_none)
    else:
        bucket = await storage.get_bucket(user=user_id)
        answer = bucket.get('answer', {"attempts": 0, "guessed": 0})
        question = bucket['question']
        variants = question['variants']
        variant_idx = int(word_index)
        if variant_idx >= len(variants):
            await query.answer()
            return
        variant_value = variants[variant_idx]
        answer['attempts'] += 1
        message = query.message
        markup = message.reply_markup

        variant_buttons = []
        for row in markup.inline_keyboard:
            for btn in row:
                if btn.callback_data and btn.callback_data.startswith("TSOb"):
                    variant_buttons.append(btn)

        if variant_idx >= len(variant_buttons):
            await query.answer()
            return

        selected_button = variant_buttons[variant_idx]
        selected_button.text = f"{'✅' if variant_value == question['word'] else '❌'} {variant_value}"
        selected_button.callback_data = TrainingSelectOneCallbackData(word_number="").pack()

        if variant_value == question['word']:
            await query.answer(Text.trainings.answer_score_100)
            answer['guessed'] += 1
            for btn in variant_buttons:
                if btn is not selected_button and btn.callback_data:
                    btn.callback_data = TrainingSelectOneCallbackData(word_number="").pack()
            await message.edit_reply_markup(reply_markup=markup)
            await asyncio.gather(
                training_send_new_question(user_id, bot),
                training_result_to_sheet(user_id, storage, bucket)
            )
            await asyncio.sleep(5)
            await message.delete()
        else:
            await storage.update_bucket(user=user_id, answer=answer)
            await message.edit_reply_markup(reply_markup=markup)
            await query.answer(Text.trainings.answer_score_0)


def register(router: Router):
    router.message.register(answer_training_type_the_answer, StateFilter(Trainings.training_type_the_answer))
    router.callback_query.register(answer_training_select_one, TrainingSelectOneCallbackData.filter(),
                                   StateFilter(Trainings.training_select_one))
