from aiogram import F, Router, types
from aiogram.filters.callback_data import CallbackData

from telegram.filters import AdminFilter
from telegram.texts import Text
from ..routine import broadcasting
from ..utils.aiogram_redis_ext import RedisStorage2ext
from ..utils.config_types import Config


async def forward_from_admin_reply(message: types.Message):
    await message.forward(message.reply_to_message.forward_from.id)


async def forward_to_admin(message: types.Message):
    config: Config = message.bot.config
    await message.answer(Text.general.forward_to_admin)
    await message.forward(config.admin_id)


class AdminBroadcastConfirm(CallbackData, prefix="admin_broadcast_message_confirm"):
    message_id: str


async def broadcast_message_confirm(message: types.Message):
    buttons = [types.InlineKeyboardButton(text=a[0], callback_data=AdminBroadcastConfirm(message_id=str(a[1])).pack())
               for a in [("No", -1), ("Yes", message.message_id)]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
    await message.reply(Text.admin.broadcast_message_confirm, reply_markup=keyboard)


async def admin_broadcast_message(query: types.CallbackQuery, storage: RedisStorage2ext,
                                  callback_data: AdminBroadcastConfirm):
    if callback_data.message_id == '-1':
        await query.answer(Text.admin.broadcast_message_confirm_no)
        await query.message.reply_to_message.delete()
    else:
        await query.answer(Text.admin.broadcast_message_confirm_yes)
        await broadcasting.broadcast_message(query.message.reply_to_message, storage)
    await query.message.delete()


def register(router: Router):
    router.message.register(forward_from_admin_reply, F.reply_to_message.forward_from, AdminFilter(admin=True))
    router.message.register(broadcast_message_confirm, AdminFilter(admin=True))
    router.callback_query.register(admin_broadcast_message, AdminBroadcastConfirm.filter())
    router.message.register(forward_to_admin)
