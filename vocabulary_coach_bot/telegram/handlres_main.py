import logging

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat
from aiogram.types.error_event import ErrorEvent

from telegram.texts import Text
from .filters import IsUserFilter
from .widgets import admin, settings, start_dialogue
from .widgets.trainigs import trainings


async def set_bot_commands(bot: Bot):
    user_commands = [BotCommand(command=k.name, description=k.value) for k in Text.commands]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeAllPrivateChats())

    admin_commands = [BotCommand(command=k.name, description=k.value) for k in Text.commands_admin]
    if admin_commands:
        admin_commands.extend(user_commands)
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=bot.config.admin_id))


async def cmd_help(message: types.Message):
    await message.answer(Text.general.help)


async def cmd_privacy(message: types.Message):
    await message.answer(Text.general.privacy)


async def errors_handler(event: ErrorEvent):
    """
    Exceptions handler. Catches all exceptions within task factory tasks.
    """
    update = event.update
    exception = event.exception
    if isinstance(exception, TelegramBadRequest):
        logging.exception(f"TelegramBadRequest: {exception} \nUpdate: {update}")
        return True
    if isinstance(exception, TelegramAPIError):
        logging.exception(f"TelegramAPIError: {exception} \nUpdate: {update}")
        return True
    logging.exception(f"Update: {update} \n{exception}")


def register_routers() -> Router:
    router = Router()

    trainings.register(router)
    settings.register(router)
    start_dialogue.register(router)

    router.message.register(cmd_help, Command(commands=["help"]))
    router.message.register(cmd_privacy, Command(commands=["privacy"]))

    admin.register(router)

    router.message.register(cmd_help, IsUserFilter(is_user=True), StateFilter(None))
    router.errors.register(errors_handler)

    return router
