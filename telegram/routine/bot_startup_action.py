import asyncio

import aioschedule
from aiogram import Dispatcher

from telegram.routine.broadcasting import broadcast_admin
from telegram.texts import Text
from telegram.widgets.trainigs.trainings_reminder import reminder_trainings


async def scheduler(bot):
    # aioschedule.every(1).seconds.do(reminder_trainings, bot=bot)
    aioschedule.every(5).minutes.do(reminder_trainings, bot=bot)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(30)
        # await asyncio.sleep(1)


async def bot_startup_action(dp: Dispatcher):
    bot = dp.bot
    dp.loop.create_task(scheduler(bot))  # доступно для динамического
    await broadcast_admin(bot, Text.general.bot_started)
