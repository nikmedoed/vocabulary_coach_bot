import typing

from aiogram import Bot

from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys
from telegram.utils.spreadsheet_connector import SpreadSheetConnector
from telegram.widgets.trainigs.trainings_generate import generate_question_message


async def training_result_to_sheet(user_id: typing.Union[int, str], storage: RedisStorage2ext, bucket: dict = None):
    if not bucket:
        bucket = await storage.get_bucket(user=user_id)
    answer = bucket.get('answer')
    if answer and int(answer['attempts']) > 0:
        answer['word'] = bucket['question']['word']
        url = await storage.get_key(StorageKeys.SHEET_URL, user=user_id)
        await SpreadSheetConnector.set_result(url, answer)


async def get_new_question(user_id: typing.Union[int, str], storage: RedisStorage2ext, qtype=None):
    url = await storage.get_key(StorageKeys.SHEET_URL, user=user_id)
    train_type = (await storage.get_state(user=user_id)).split(":")[-1]
    question = await getattr(SpreadSheetConnector, train_type)(url)
    await storage.update_bucket(user=user_id, question=question, answer={"attempts": 0, "guessed": 0})
    return question, train_type


async def training_send_new_question(user_id: typing.Union[int, str],
                                     bot: Bot,
                                     storage: RedisStorage2ext = None):
    storage: RedisStorage2ext = storage or bot.get("storage")
    question, train_type = await get_new_question(user_id, storage)
    reply = await bot.send_message(user_id, **generate_question_message(question, train_type))
    await storage.set_key(StorageKeys.CURRENT_QUESTION_ID, reply.message_id, user=user_id)
    return reply


