import csv
import io

import aiosqlite
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, Document

from bot.config import get_config
from bot.services.routes import save_route_in_db
from bot.storage.db import get_all_orders, get_paid_orders, mark_ticket_sent, get_user_id_by_order_id, mark_order_paid, \
    mark_order_canceled

config = get_config()

admin_router = Router()

pending_ticket_uploads = {}  # key: admin_id, value: order_id

# For manual manager status of order
@admin_router.message(Command("mark_paid"))
async def set_paid_manual_order(message: Message):
    if not str(message.from_user.id) in config.admin_ids:
        await message.answer("❌ Unauthorized.")
        return

    try:
        order_id = int(message.text.split()[1])
        await mark_order_paid(order_id)
        await message.answer(f"Order {order_id} has paid!")
    except:
        await message.answer("❗ Usage: /mark_paid <order_id>")


@admin_router.message(Command("cancel_order"))
async def set_canceled_unpaid_order(message: Message):
    if not str(message.from_user.id) in config.admin_ids:
        await message.answer("❌ Unauthorized.")
        return
    try:
        order_id = int(message.text.split()[1])
        await mark_order_canceled(order_id)
        await message.answer(f"Order {order_id} has canceled!")
    except:
        await message.answer("❗ Usage: /cancel_order <order_id>")


@admin_router.message(Command("add_route"))
async def update_routes(message: Message):
    if not str(message.from_user.id) in config.admin_ids:
        await message.answer("❌ Unauthorized.")
        return

    try:
        _, dep, dest, cost = message.text.strip().split()
        cost = float(cost)
        await save_route_in_db(dep, dest, cost)
        await message.answer(f"✅ Route {dep} → {dest} added with price {cost} USDT.")
    except Exception as e:
        print(e)  # debug
        await message.answer("❗ Usage: /add_route <departure> <destination> <price>")

@admin_router.message(Command("attach_invoice"))
async def prepare_ticket_upload(message: Message):
    if not str(message.from_user.id) in config.admin_ids:
        await message.answer("❌ Unauthorized.")
        return

    try:
        order_id = int(message.text.split()[1])
        pending_ticket_uploads[message.from_user.id] = order_id
        await message.answer(f"📎 Upload the PDF ticket for Order #{order_id}.")
    except:
        await message.answer("❗ Usage: /attach_invoice <order_id>")

@admin_router.message(F.document)
async def handle_pdf_upload(message: Message, bot: Bot):
    admin_id = message.from_user.id
    if not str(admin_id) in config.admin_ids:
        return  # Not attaching anything

    #  Check if there's a pending upload
    if admin_id not in pending_ticket_uploads:
        return await message.answer("⚠️ No pending ticket upload found.")

    order_id = pending_ticket_uploads.pop(admin_id)

    # Get user info from DB
    user_id = await get_user_id_by_order_id(order_id)
    if user_id is None:
        return await message.answer("❌ Order not found.")

    # Send ticket to user
    await bot.send_document(
        chat_id=int(user_id),
        document=message.document.file_id,
        caption="🎟 Your ticket PDF is ready!"
    )

    await message.answer("✅ Ticket sent to user.")
    # Update DB
    await mark_ticket_sent(order_id=order_id)


@admin_router.message(Command("orders"))
async def get_orders(message: Message):
    if not str(message.from_user.id) in config.admin_ids:
        await message.answer("🚫 You are not authorized.")
        return

    orders = await get_all_orders()
    if not orders:
        await message.answer("📭 No orders yet.")
        return

    for number, order in enumerate(orders, 1):
        answer_text = (
            f"🧾 <b>Order #{number}</b>\n"
            f"User: @{order['username'] or 'Unknown'}\n"
            f"From: {order['departure']} ➡ {order['destination']}\n"
            f"Date: {order['travel_date']}\n"
            f"Seat: {order['seat_type']}\n"
            f"Price: {order['price']} USDT\n"
            f"Invoice url: {order['invoice_id']}\n"
            f"Status:<b>{order['status']}</b>\n"
        )

        await message.answer(answer_text)


@admin_router.message(Command("export_paid"))
async def export_paid_orders(message: Message):
    if not str(message.from_user.id) in config.admin_ids:
        await message.answer("🚫 You are not authorized.")
        return

    orders = await get_paid_orders()
    if not orders:
        await message.answer("No paid orders found.")
        return

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=orders[0].keys())
    writer.writeheader()
    for row in orders:
        writer.writerow(dict(row))

    output.seek(0)
    with open("paid_orders.csv", "w", encoding="utf-8") as f:
        f.write(output.read())

    await message.answer_document(FSInputFile("paid_orders.csv"), caption="📦 Paid orders exported.")
