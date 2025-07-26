import asyncio
import datetime

from aiogram import Bot

from bot.services.crypto import get_invoice_status
from bot.storage.db import get_unpaid_orders, mark_order_paid, mark_order_canceled


async def monitor_payments(bot: Bot):
    while True:
        unpaid_orders = await get_unpaid_orders()
        time_now = datetime.datetime.utcnow()

        for order in unpaid_orders:
            status = await get_invoice_status(order["invoice_id"])

            if status == "paid":
                await bot.send_message(
                    order["user_id"],
                    "✅ Payment received. Your ticket is confirmed!"
                )
                await mark_order_paid(order["id"])

                continue

            # Check expiration
            created_time = datetime.datetime.strptime(order["created_time"], "%Y-%m-%d %H:%M:%S")
            if (time_now - created_time).total_seconds() > (60 * 60):  # 60min
                await mark_order_canceled(order["id"])
                try:
                    await bot.send_message(
                        order["user_id"],
                        "⌛ Your ticket was canceled due to unpaid status after 60 minutes."
                    )
                except Exception as e:
                    print(e)  # debug
                    pass  # if user force stop the bot

        await asyncio.sleep(30)  # check every 30 seconds
