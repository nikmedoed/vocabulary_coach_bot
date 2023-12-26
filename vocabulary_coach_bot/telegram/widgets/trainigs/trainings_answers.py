import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from rapidfuzz import fuzz

from telegram.texts import Text
from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys
from telegram.widgets.trainigs.trainings_common import training_result_to_sheet, training_send_new_question
from telegram.widgets.trainigs.trainings_generate import Trainings, training_select_one_button

ANSWERS = {int(i[len('answer_score_'):]): str(k) for i, k in Text.trainings.__dict__.items() if
           i.startswith('answer_score_')}


async def answer_training_type_the_answer(message: types.Message, storage: RedisStorage2ext, state: FSMContext):
    user_id = message.from_user.id
    bot = message.bot
    bucket = await storage.get_bucket(user=user_id)
    question = bucket.get('question')
    score = fuzz.QRatio(question['word'], message.text)

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
    await asyncio.gather(*post_actions)


async def answer_training_select_one(query: types.CallbackQuery, storage: RedisStorage2ext, state: FSMContext,
                                     callback_data: dict):
    user_id = query.from_user.id
    bot = query.bot
    word = callback_data['word_number']
    if not word:
        await query.answer(Text.trainings.answer_select_one_none)
    else:
        bucket = await storage.get_bucket(user=user_id)
        answer = bucket.get('answer', {"attempts": 0, "guessed": 0})
        word = bucket['question']['variants'][int(word)]
        answer['attempts'] += 1
        message = query.message
        markup = message.reply_markup
        keys = markup.inline_keyboard
        if word == bucket['question']['word']:
            await query.answer(Text.trainings.answer_score_100)
            for row in keys:
                for m in row:
                    if m.text.endswith(word):
                        m.text = f"✅ {word}"
                    m.callback_data = training_select_one_button.new(word_number="")
            answer['guessed'] += 1
            await asyncio.gather(
                message.edit_reply_markup(markup),
                training_send_new_question(user_id, bot),
                training_result_to_sheet(user_id, storage, bucket)
            )
            await asyncio.sleep(5)
            await message.delete()
        else:
            await storage.update_bucket(user=user_id, answer=answer)
            for row in keys:
                for m in row:
                    if m.text.endswith(word):
                        m.text = f"❌ {word}"
                        m.callback_data = training_select_one_button.new(word_number="")
            await asyncio.gather(
                message.edit_reply_markup(markup),
                query.answer(Text.trainings.answer_score_0)
            )


def register(dispatcher: Dispatcher):
    dispatcher.register_message_handler(answer_training_type_the_answer,
                                        state=Trainings.training_type_the_answer)

    dispatcher.register_callback_query_handler(answer_training_select_one,
                                               training_select_one_button.filter(),
                                               state=Trainings.training_select_one)
