import csv
import io
from functools import wraps

from loguru import logger

from aiogram import Router, F, Bot
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


class NoBookingsFound(Exception): ...
class ExportFailed(Exception): ...
class PendingUploadNotFound(Exception): ...
class BookingNotFound(Exception): ...
class UserIdNotFound(Exception): ...


def admin_required(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if str(message.from_user.id) not in config.ADMIN_IDS:
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

    try:
        # 1. Get bookings
        bookings = await booking_dao.find_all()
        if not bookings:
            raise NoBookingsFound()

        # 2. Prepare CSV in-memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=bookings[0].to_dict().keys())
        writer.writeheader()
        for row in bookings:
            writer.writerow(row.to_dict())

        output.seek(0)

        # 3. Save file locally (avoid open() twice)
        file_path = "export_bookings.csv"
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.write(output.read())

        # 4. Send document to admin
        await message.answer_document(
            FSInputFile(file_path),
            caption="📦 All bookings exported."
        )

    except NoBookingsFound:
        await message.answer("📭 No bookings found.")
    except Exception as e:
        logger.error(f"Error during export_bookings: {e}")
        await message.answer("❌ Failed to export bookings. Try again later.")


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


@admin_router.message(Command("attach_invoice"))
@admin_required
async def prepare_ticket_upload(message: Message):
    try:
        booking_id = int(message.text.split()[1])
        pending_ticket_uploads[message.from_user.id] = booking_id
        await message.answer(f"📎 Upload the PDF ticket for Order #{booking_id}.")
    except Exception as e:
        logger.error(f"Get error in prepare_ticket_upload method: {e}")
        await message.answer("❗ Usage: /attach_invoice <order_id>")


@admin_router.message(F.document)
@admin_required
async def handle_pdf_upload(message: Message, session: AsyncSession, dao: dict):
    admin_id = message.from_user.id
    booking_dao: BookingDAO = dao["booking"]

    try:
        # Get pending booking id
        booking_id = pending_ticket_uploads.get(admin_id)
        if booking_id is None:
            raise PendingUploadNotFound()

        booking = await booking_dao.find_one_or_none_by_id(data_id=booking_id)
        if not booking:
            raise BookingNotFound(booking_id)

        if not booking.user_id:
            raise UserIdNotFound(booking_id)

        # Only remove from pending when we're sure booking is valid
        pending_ticket_uploads.pop(admin_id)

        # Send ticket
        await message.bot.send_document(
            chat_id=int(booking.user_id),
            document=message.document.file_id,
            caption="🎟 Your ticket PDF is ready!"
        )

        # Update DB
        await booking_dao.update(
            filters=BookingBase(id=booking_id),
            values=BookingByStatus(status="processed")
        )

        await message.answer("✅ Ticket sent to user.")

    except PendingUploadNotFound:
        await message.answer("⚠️ No pending ticket upload found.")
    except BookingNotFound as e:
        await message.answer(f"⚠️ Booking {e} not found.")
    except UserIdNotFound as e:
        await message.answer(f"⚠️ Booking {e} has no user assigned.")
    except Exception as e:
        logger.error(f"Unexpected error in ticket upload: {e}")
        await message.answer("❌ Something went wrong while sending ticket.")
