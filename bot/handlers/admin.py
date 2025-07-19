import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from bot.storage import get_all_orders

load_dotenv()

admin_router = Router()


@admin_router.message(Command("orders"))
async def get_orders(message: Message):
    if not str(message.from_user.id) in os.getenv("ADMIN_IDS"):
        await message.answer("🚫 You are not authorized.")
        return

    orders = get_all_orders()
    if not orders:
        await message.answer("📭 No orders yet.")
        return

    answer_text = ""
    for number, order in enumerate(orders, 1):
        answer_text = (
            f"🧾 <b>Order #{number}</b>\n"
            f"User: @{order.get('username', 'Unknown')}\n"
            f"From: {order['departure']} ➡ {order['destination']}\n"
            f"Date: {order['travel_date']}\n"
            f"Seat: {order['seat_type']}\n"
            f"Price: {order['price']} USDT\n"
            f"Invoice url: {order['invoice_url']}\n"
            f"Create date: {order['create_date']}\n"
        )

    await message.answer(answer_text)
