from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Dispatcher
from telegram.routine.broadcasting import broadcast_admin
from telegram.texts import Text
from telegram.widgets.trainigs.trainings_reminder import reminder_trainings
from telegram.utils.database_update import user_database_update


async def scheduler(dp: Dispatcher):
    bot = dp.bot
    scheduler = AsyncIOScheduler()
    scheduler.add_job(reminder_trainings, 'interval',  minutes=5, args=[bot])
    scheduler.start()


async def bot_startup_action(dp: Dispatcher):
    bot = dp.bot
    await scheduler(dp)
    await broadcast_admin(bot, Text.general.bot_started)
    await user_database_update(bot)
