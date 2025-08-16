import csv
import io
from functools import wraps

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession


from bot.config import config
from bot.database.dao.dao import BookingDAO
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
async def export_paid_orders(message: Message, data: dict):
    dao: BookingDAO = data["booking"]
    bookings = await dao.find_all()

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
