from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from bot.config import get_config
from bot.keyboards.default import general_keyboard_menu

user_router = Router()

config = get_config()


@user_router.message(CommandStart())
async def welcome_massage(message: Message) -> None:
    await message.answer(
        "👋 Welcome to Ticket Bot!",
        reply_markup=general_keyboard_menu()
    )


@user_router.message(Command("help"))
async def get_help(message: Message):
    supports = "\n".join(config.supports)

    await message.answer(
        f"ALl supports here:\n{supports}"
    )
