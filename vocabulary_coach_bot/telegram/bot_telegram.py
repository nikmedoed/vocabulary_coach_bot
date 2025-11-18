import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from .handlres_main import register_routers, set_bot_commands
from .middleware import register_middleware
from .utils.aiogram_redis_ext import RedisStorage2ext
from .utils.config_types import Config, RedisConfig
from telegram.routine.bot_startup_action import bot_startup_action

asyncio.Semaphore(20)


async def main(config):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    storage = RedisStorage2ext(**config.redis_conf.__dict__)

    bot = Bot(
        config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    me = await bot.get_me()
    storage.set_bot_id(me.id)

    bot.config: Config = config
    bot.storage = storage

    dp = Dispatcher(storage=storage)

    router = register_routers()
    register_middleware(router)
    dp.include_router(router)
    try:
        await set_bot_commands(bot)
        await bot_startup_action(bot)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()


def main_run(config):
    try:
        asyncio.run(main(config))
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
