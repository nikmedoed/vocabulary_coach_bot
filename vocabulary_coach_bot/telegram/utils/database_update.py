import asyncio
from aiogram import Bot
from .config_types import Config
from .aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys
from telegram.texts import Text
import logging
from telegram.utils.spreadsheet_connector import SpreadSheetConnector

DATABASE_VERSION = '1.1'


async def check_user_base_version(bot, user, sheet_url):
    storage: RedisStorage2ext = bot["storage"]
    if sheet_url:
        version = await SpreadSheetConnector.check_version(sheet_url)
        if version != DATABASE_VERSION:
            await storage.set_state(user=user)
            await storage.set_key(StorageKeys.SHEET_URL, "", chat=user)
            await bot.send_message(user, Text.start.database_old_version)
    else:
        reminded = await storage.get_key(StorageKeys.SEND_SHEET_REMIND, chat=user)
        if reminded:
            await storage.delete_user_data(user)
        else:
            await storage.set_key(StorageKeys.SEND_SHEET_REMIND, True, chat=user)
            await bot.send_message(user, Text.start.database_no_link)


async def user_database_update(bot: Bot):
    config: Config = bot.get('config')
    storage: RedisStorage2ext = bot["storage"]
    users = await storage.get_all_users_values()

    for u, v in users.items():
        try:
            await check_user_base_version(bot, u, v.get(StorageKeys.SHEET_URL.name))
        except Exception as e:
            logging.error(f"user_database_update - {e.__class__}: {e} {u, v}")
