import asyncio
from collections import defaultdict, deque

from telegram.utils.spreadsheet_connector import SpreadSheetConnector


# Здесь уместо использовать монго, если начнутся проблемы с памятью

class TrainingsChache:
    chache = defaultdict(lambda: defaultdict(deque))

    async def extend_user_que(self, user_que, coro):
        data = await coro
        if not data:
            return

        if isinstance(data, list):
            valid_data = [item for item in data if 'question' in item]
            user_que.extend(valid_data)
        elif 'question' in data:
            user_que.append(data)

    async def get_question(self, user, train_type, url):
        question_request = getattr(SpreadSheetConnector, train_type)
        user_que = self.chache[user][train_type]

        question = None
        while not question:
            if len(user_que) > 0:
                question = user_que.popleft()
            else:
                question = await question_request(url)
                if not question or 'question' not in question:
                    question = None

            if not question:
                await asyncio.sleep(0.5)

        count = 5 - len(user_que)
        if count > 0:
            task = asyncio.get_event_loop().create_task(
                self.extend_user_que(user_que, question_request(url, count))
            )
            task.add_done_callback(
                lambda t: t.result() if t.exception() is None else print(f"Task error: {t.exception()}"))

        return question


TRAININGS_CHACHE = TrainingsChache()
