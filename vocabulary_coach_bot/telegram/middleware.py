import datetime
import logging
from typing import Union

from aiogram import types, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.utils.exceptions import MessageError

from telegram.utils.aiogram_redis_ext import RedisStorage2ext
from telegram.utils.constants import StorageKeys


class SheetConnectMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    async def pre_process(self, obj, data, *args):
        storage: RedisStorage2ext = obj.bot["storage"]
        data["sheet_url"] = await storage.get_key(StorageKeys.SHEET_URL, user=obj.from_user.id)


class ActivityMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update", "edited", "pool", "member"]

    async def pre_process(self, obj: Union[types.Message, types.CallbackQuery], data, *args):
        try:
            storage: RedisStorage2ext = obj.bot["storage"]
            await storage.set_key(
                key=StorageKeys.PREVIOUS_MESSAGE_DATE,
                user=obj.from_user.id,
                value=round(datetime.datetime.now().timestamp())
            )
            data["storage"] = storage
        except MessageError as e:  # MessageNotModified
            logging.error(f"ActivityMiddleware - {e.__class__}: {e.text}")


class PreviosMessageMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update", "query", "edited", "pool", "member"]

    async def pre_process(self, obj: Union[types.Message, types.CallbackQuery], data, *args):
        chat_id = obj.from_user.id
        bucket = await self.manager.storage.get_bucket(user=chat_id)
        message_id = bucket.get("previous_message_id")
        if message_id:
            try:
                await self.manager.storage.update_bucket(
                    user=chat_id,
                    previous_message_id=None,
                )
                await obj.bot.edit_message_reply_markup(
                    chat_id, message_id,
                    reply_markup=None
                )
            except MessageError as e:  # MessageNotModified
                logging.error(f"PreviosMessageMiddleware - {e.__class__}: {e.text}")
        data['save_id_to_clear_inline'] = self.save_id_to_clear_inline(obj.from_user.id)

    def save_id_to_clear_inline(self, user_id):
        """
        Generate function for storing previous message id from user. User is setted by middleware.
        Message id will be used for clearing inline keyboard.
        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        return lambda message_id: self.manager.storage.update_bucket(
            user=user_id,
            previous_message_id=message_id,
        )


async def register_middleware(dp: Dispatcher):
    # config: Config = dp.bot.get("config")

    dp.middleware.setup(LoggingMiddleware())
    dp.middleware.setup(ActivityMiddleware())
    dp.middleware.setup(SheetConnectMiddleware())
    # dp.middleware.setup(PreviosMessageMiddleware())
