import csv
import io
from functools import wraps

from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession


from bot.config import config
from bot.database.dao.dao import BookingDAO, RouteDAO
from bot.database.schemas.booking import BookingByStatus, BookingBase
from bot.database.schemas.route import RouteCreate
from bot.keyboards.admin import admin_general_keyboard_menu

admin_router = Router()

pending_ticket_uploads = {}  # key: admin_id, value: order_id ?


def admin_required(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if str(message.from_user.id) not in config.admin_ids:
            await message.answer("🚫 You are not authorized.")
            return
        return await handler(message, *args, **kwargs)
    return wrapper


@admin_router.message(Command("admin"))
@admin_required
async def get_admin_panel(message: Message):
    await message.answer(
        "Admin authorized.",
        reply_markup=admin_general_keyboard_menu()
    )


@admin_router.message(Command("export_bookings"))
@admin_required
async def export_paid_orders(message: Message, session: AsyncSession, dao: dict):
    booking_dao: BookingDAO = dao["booking"]
    bookings = await booking_dao.find_all()

    if not bookings:
        await message.answer("No bookings found.")
        return

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=bookings[0].to_dict().keys()
    )
    writer.writeheader()
    for row in bookings:
        writer.writerow(row.to_dict())

    output.seek(0)
    with open("export_bookings.csv", "w", encoding="utf-8") as f:
        f.write(output.read())

    await message.answer_document(
        FSInputFile("export_bookings.csv"),
        caption="📦 All bookings exported."
    )


@admin_router.message(Command("add_route"))
@admin_required
async def update_routes(message: Message, session: AsyncSession, dao: dict):
    try:
        _, dep, dest, cost = message.text.strip().split()
        cost = float(cost)
        route_dao: RouteDAO = dao["route"]
        await route_dao.add(
            RouteCreate(departure=dep, destination=dest, cost=cost)
        )
        await message.answer(f"✅ Route {dep} → {dest} added with price {cost} USDT.")
    except Exception as e:
        logger.error(f"Get error in add_route method: {e}")
        await message.answer("❗ Usage: /add_route <departure> <destination> <price>")


# For manual manager booking status
@admin_router.message(Command("mark_paid"))
@admin_required
async def set_paid_booking(message: Message, session: AsyncSession, dao: dict):
    try:

        booking_id = int(message.text.split()[1])
        booking_dao: BookingDAO = dao["booking"]
        await booking_dao.update(filters=BookingBase(id=booking_id), values=BookingByStatus(status="paid"))
        await message.answer(f"Order {booking_id} has paid!")
    except Exception as e:
        logger.error(f"Get error in mark_paid method: {e}")
        await message.answer("❗ Usage: /mark_paid <order_id>")


@admin_router.message(Command("cancel_order"))
@admin_required
async def set_canceled_booking(message: Message, session: AsyncSession, dao: dict):
    try:
        booking_id = int(message.text.split()[1])
        booking_dao: BookingDAO = dao["booking"]
        await booking_dao.update(filters=BookingBase(id=booking_id), values=BookingByStatus(status="canceled"))
        await message.answer(f"Order {booking_id} has canceled!")
    except Exception as e:
        logger.error(f"Get error in set_canceled_booking method: {e}")
        await message.answer("❗ Usage: /cancel_order <order_id>")
