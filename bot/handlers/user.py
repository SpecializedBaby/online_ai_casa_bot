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
    """Handle /start command and register user if not exists."""
    user_id = message.from_user.id
    dao: UserDAO = dao["user"]

    try:
        user = await dao.find_one_or_none_by_id(data_id=user_id)

        if user:
            # Existing user
            await message.answer(
                f"👋 Welcome back, {message.from_user.full_name}! "
                f"Choose a command from the menu.",
                reply_markup=general_keyboard_menu()
            )
            return

        # New user → register
        user_data = UserCreate(
            id=user_id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        await dao.add(data=user_data)

        await message.answer(
            f"👋 Welcome to Ticket Bot, {message.from_user.full_name}!\n"
            f"🎉 Thanks for registering!",
            reply_markup=general_keyboard_menu()
        )

    except Exception as e:
        logger.error(f"Error in /start for user {user_id}: {e}", exc_info=True)
        await message.answer("❌ Something went wrong. Please try again later.")


@user_router.message(Command("my_bookings"))
async def user_order_history(message: Message, session: AsyncSession, dao: dict):
    """Handle /my_bookings command and show paid bookings."""
    dao: BookingDAO = dao["booking"]

    try:
        bookings = await dao.find_all(
            BookingsByUser(user_id=message.from_user.id, status="paid")
        )

        if not bookings:
            await message.answer("📭 You don’t have any paid bookings yet.")
            return

        # Build message text
        text_lines = []
        for i, booking in enumerate(bookings, start=1):
            text_lines.append(
                f"🎫 <b>Booking #{i}</b>\n"
                f"From: {booking.route.departure} ➡ {booking.route.destination}\n"
                f"Date: {booking.date}\n"
                f"Seat: {booking.seat_type}\n"
                f"Tickets: {booking.quantity}\n"
                f"Price: {booking.price} USDT\n"
            )

        await message.answer("\n".join(text_lines))

    except Exception as e:
        logger.error(f"Error in /my_bookings for user {message.from_user.id}: {e}", exc_info=True)
        await message.answer("❌ Could not fetch your bookings. Please try again later.")



