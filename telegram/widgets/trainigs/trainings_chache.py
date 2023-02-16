from collections import defaultdict, deque
from telegram.utils.spreadsheet_connector import SpreadSheetConnector
import asyncio

# здесь уместо использовать монго, если начнутся проблемы с памятью

class TrainingsChache:
    chache = defaultdict(lambda: defaultdict(deque))

    async def extend_user_que(self, user_que, coro):
        data = await coro
        if type (data) != list:
            user_que.append(data)
        else:
            user_que.extend(data)

    async def get_question(self, user, train_type, url):
        question_request = getattr(SpreadSheetConnector, train_type)
        user_que = self.chache[user][train_type]
        if len(user_que) > 0:
            question = user_que.popleft()
        else:
            question = await question_request(url)
        count = 5 - len(user_que)
        if count > 0:
            asyncio.get_event_loop().create_task(
                self.extend_user_que(user_que, question_request(url, count))
            )
        return question


TRAININGS_CHACHE = TrainingsChache()
