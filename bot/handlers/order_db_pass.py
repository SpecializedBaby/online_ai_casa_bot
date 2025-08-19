from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.dao.dao import BookingDAO
from bot.database.schemas.booking import BookingsByUser


order_db_router = Router()


@order_db_router.message(Command("db_pass"))
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