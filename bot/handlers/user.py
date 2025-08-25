from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import broker
from bot.database.dao.dao import UserDAO, BookingDAO, MonthlyPassDAO
from bot.database.schemas.user import UserCreate
from bot.database.schemas.monthly_pass import PassStatus
from bot.keyboards.user import general_keyboard_menu

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, dao: dict):
    """Handle /start command and register user if not exists."""
    user_id = message.from_user.id
    user_dao: UserDAO = dao["user"]

    try:
        user = await user_dao.find_one_or_none_by_id(data_id=user_id)

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
            full_name=message.from_user.full_name
        )
        await user_dao.add(data=user_data)

        await message.answer(
            f"👋 Welcome to Ticket Bot, {message.from_user.full_name}!\n"
            f"🎉 Thanks for registering!",
            reply_markup=general_keyboard_menu()
        )
        # Включаем рекламные оповещения
        await broker.publish(message=user_id, queue="noti_user")

    except Exception as e:
        logger.error(f"Error in /start for user {user_id}: {e}", exc_info=True)
        await message.answer("❌ Something went wrong. Please try again later.")


@user_router.message(Command("my_offers"))
async def user_ordered_offers(message: Message, session: AsyncSession, dao: dict):
    """Handle /my_offers command and show all offers for user."""
    pass_dao: MonthlyPassDAO = dao["pass"]

    try:
        passes = await pass_dao.find_all(filters=PassStatus(status="paid"))
        if not passes:
            await message.answer(f" ❌ You dont have any offers yet!")
            return

        text_lines = []
        for i, _pass in enumerate(passes, start=1):
            text_lines.append(
                f"🎫 <b>Monthly Pass #{i}</b>\n"
                f"Pass name: {_pass.offer.name}"
                f"Month: {_pass.month}\n"
                f"Status: {_pass.status}"
            )
        await message.answer("\n".join(text_lines))
    except Exception as e:
        logger.error(f"Error in /my_offers for user {message.from_user.id}: {e}", exc_info=True)
        await message.answer("❌ Could not fetch your bookings. Please try again later.")


@user_router.message(Command("my_bookings"))
async def user_order_history(message: Message, session: AsyncSession, dao: dict):
    """Handle /my_bookings command and show paid bookings."""
    booking_dao: BookingDAO = dao["booking"]

    try:
        bookings = await booking_dao.get_booking_paid(user_id=message.from_user.id)

        if not bookings:
            await message.answer("You don't have bookings yet!")
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
