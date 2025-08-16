from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.keyboards.admin import admin_general_keyboard_menu

admin_router = Router()


@admin_router.message(Command("admin"))
async def get_admin_panel(message: Message):
    if not str(message.from_user.id) in config.admin_ids:
        await message.answer("❌ Unauthorized.")
        return

    await message.answer(
        "Admin authorized.",
        reply_markup=admin_general_keyboard_menu()
    )
