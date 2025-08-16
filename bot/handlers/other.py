from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import config

other_router = Router()


@other_router.message(Command("help"))
async def get_help(message: Message):
    supports = "\n".join(config.supports)

    await message.answer(
        f"ALl supports here:\n{supports}"
    )
