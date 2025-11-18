import asyncio
import logging
from collections import defaultdict, deque

from telegram.utils.spreadsheet_connector import SpreadSheetConnector


# Здесь уместо использовать базу, если начнутся проблемы с памятью

class TrainingsChache:
    chache = defaultdict(lambda: defaultdict(deque))

    async def extend_user_que(self, user_que, coro):
        data = await coro
        if not data:
            return

        if isinstance(data, dict) and data.get("error"):
            logging.error(f"Trainings cache preload error: {data}")
            return

        if isinstance(data, list):
            valid_data = [item for item in data if 'question' in item]
            user_que.extend(valid_data)
        elif isinstance(data, dict) and 'question' in data:
            user_que.append(data)

    async def get_question(self, user, train_type, url):
        question_request = getattr(SpreadSheetConnector, train_type)
        user_que = self.chache[user][train_type]

        attempts = 0
        question = None
        while not question and attempts < 20:
            attempts += 1
            if len(user_que) > 0:
                question = user_que.popleft()
            else:
                question = await question_request(url)
                if not question or 'question' not in question:
                    if isinstance(question, dict) and question.get("error"):
                        logging.error(f"Trainings cache error for user {user}: {question}")
                    question = None

            if not question:
                await asyncio.sleep(0.5)

        if not question:
            raise RuntimeError("Не удалось получить вопрос из таблицы")

        count = 5 - len(user_que)
        if count > 0:
            task = asyncio.get_event_loop().create_task(
                self.extend_user_que(user_que, question_request(url, count))
            )
            task.add_done_callback(
                lambda t: t.result() if t.exception() is None else logging.error(f"Task error: {t.exception()}"))

        return question


TRAININGS_CHACHE = TrainingsChache()
