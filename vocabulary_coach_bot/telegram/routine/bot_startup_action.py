from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from telegram.routine.broadcasting import broadcast_admin
from telegram.texts import Text
from telegram.widgets.trainigs.trainings_reminder import reminder_trainings
from telegram.utils.database_update import user_database_update


async def scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(reminder_trainings, 'interval',  minutes=5, args=[bot])
    scheduler.start()


async def bot_startup_action(bot: Bot):
    await scheduler(bot)
    await broadcast_admin(bot, Text.general.bot_started)
    await user_database_update(bot)
