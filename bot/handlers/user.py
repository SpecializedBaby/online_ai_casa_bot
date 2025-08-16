from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.dao.dao import UserDAO, BookingDAO
from bot.database.schemas.booking import BookingsByUser
from bot.database.schemas.user import UserCreate
from bot.keyboards.user import general_keyboard_menu

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

        msg = f"🎉 Thanks for register!{message.from_user.full_name}."

        await message.answer(
            f"👋 Welcome to Ticket Bot!\n{msg}",
            reply_markup=general_keyboard_menu()
        )

    except Exception as e:
        logger.error(f"Error /start for user {message.from_user.id}: {e}")
        await message.answer("You get error. Try again later.")


@user_router.message(Command("my_bookings"))
async def user_order_history(message: Message, session: AsyncSession, dao: dict):
    dao: BookingDAO = dao["booking"]
    bookings = await dao.find_all(
        BookingsByUser(
            user_id=message.from_user.id,
            status="paid"
        )
    )

    if not bookings:
        await message.answer("📭 You have not paid bookings.")
        return

    text = ""
    for i, o in enumerate(bookings, 1):
        text += (
            f"🎫 <b>Booking #{i}</b>\n"
            f"From: {o.route.departure} ➡ {o.route.destination}\n"
            f"Date: {o.date}\n"
            f"Seat: {o.seat_type}\n"
            f"Tickets: {o.quantity}\n"
            f"Price: {o.price} USDT\n\n"
        )

    await message.answer(text)
