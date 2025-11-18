import datetime
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram import types
from aiogram.exceptions import TelegramBadRequest

from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys


class SheetConnectMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        if hasattr(event, "from_user") and event.from_user:
            storage: RedisStorage2ext = data["bot"].storage
            data["sheet_url"] = await storage.get_key(StorageKeys.SHEET_URL, user=event.from_user.id)
        return await handler(event, data)


class ActivityMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        try:
            storage: RedisStorage2ext = data["bot"].storage
            if hasattr(event, "from_user") and event.from_user:
                await storage.set_key(
                    key=StorageKeys.PREVIOUS_MESSAGE_DATE,
                    user=event.from_user.id,
                    value=round(datetime.datetime.now().timestamp())
                )
            data["storage"] = storage
        except Exception as e:
            logging.error(f"ActivityMiddleware error: {e}")
        return await handler(event, data)


class PreviosMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        bot: Bot = data["bot"]
        storage: RedisStorage2ext = bot.storage

        if not getattr(event, "from_user", None):
            return await handler(event, data)

        chat_id = event.from_user.id

        bucket = await storage.get_bucket(user=chat_id)
        message_id = bucket.get("previous_message_id")
        if message_id:
            try:
                await storage.update_bucket(user=chat_id, previous_message_id=None)
                await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
            except TelegramBadRequest as e:
                logging.error(
                    "PreviosMessageMiddleware - %s: %s",
                    e.__class__.__name__,
                    e,
                )

        data["save_id_to_clear_inline"] = lambda msg_id, uid=chat_id: storage.update_bucket(
            user=uid,
            previous_message_id=msg_id,
        )

        return await handler(event, data)


def register_middleware(router):
    am = ActivityMiddleware()
    router.message.middleware.register(am)
    router.callback_query.middleware.register(am)

    sc = SheetConnectMiddleware()
    router.message.middleware.register(sc)
    router.callback_query.middleware.register(sc)

    # previos = PreviosMessageMiddleware()
    # router.message.middleware.register(previos)
    # router.callback_query.middleware.register(previos)
