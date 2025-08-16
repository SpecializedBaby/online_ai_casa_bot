from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.dao.dao import UserDAO
from bot.database.schemas.user import UserCreate
from bot.keyboards.default import general_keyboard_menu

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, dao: dict):
    try:
        user_id = message.from_user.id
        dao: UserDAO = dao["user"]
        user_info = await dao.find_one_or_none_by_id(data_id=user_id)

        if user_info:
            await message.answer(
                f"👋 Welcome, {message.from_user.full_name}! Make command.",
                reply_markup=general_keyboard_menu()
            )
            return

        user_data = UserCreate(
            id=user_id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        await dao.add(data=user_data)

        # Формирование сообщения
        msg = f"🎉 Thanks for register!{message.from_user.full_name}."

        await message.answer(
            f"👋 Welcome to Ticket Bot!\n{msg}",
            reply_markup=general_keyboard_menu()
        )

    except Exception as e:
        logger.error(f"Error /start for user {message.from_user.id}: {e}")
        await message.answer("You get error. Try again later.")
