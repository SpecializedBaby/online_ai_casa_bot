import asyncio
import datetime

from aiogram import Bot

from bot.config import config
from bot.services.crypto import get_invoice_status

ADMIN_IDS = config.admin_ids

async def monitor_payments(bot: Bot):
    while True:
        unpaid_orders = await get_unpaid_orders()
        time_now = datetime.datetime.utcnow()

        # Order monitor
        for order in unpaid_orders:
            if order["payment_method"] == "pay_cryptobot":
                status = await get_invoice_status(order["invoice_id"])

                if status == "paid":
                    await user_notification_paid_order(user_id=order["user_id"], bot=bot)
                    await mark_order_paid(order["id"])
                    await admin_notification_paid_order(order=order, bot=bot)
                    await mark_notified_admin(order["id"])
                    continue

            elif order["payment_method"] == "pay_manual" and not order["notified"]:
                await admin_notification_manual_order(order=order, bot=bot)
                await mark_notified_admin(order["id"])
            # Order what didnt found route
            elif not order["notified"] and order["price"] is None:
                await admin_notification_not_route(order=order, bot=bot)
                await mark_notified_admin(order["id"])

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


async def user_notification_paid_order(user_id: int, bot: Bot):
    await bot.send_message(
        user_id,
        "✅ Payment received. Your ticket is confirmed!",
        reply_markup=general_keyboard_menu()
    )


async def admin_notification_paid_order(order: dict, bot: Bot) -> None:
    # Admin Notification about new paid order
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"📬 New PAID order id:{order['id']}!\n\n"
            f"User: @{order['username']} ({order['user_id']})\n"
            f"Route: {order['departure']} → {order['destination']}\n"
            f"Quantity: {order['quantity']}\n"
            f"Total: {order['price']} USDT"
        )


async def admin_notification_manual_order(order: dict, bot: Bot) -> None:
    # Admin Notification about new order with manual payment
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            "📥 New MANUAL PAYMENT order waiting:\n\n"
                f"👤 @{order['username']} ({order['user_id']})\n"
                f"🛤 {order['departure']} → {order['destination']}\n"
                f"👥 Quantity: {order['quantity']}\n"
                f"💰 Price: {order['price']} USDT\n"
                f"🕐 Date: {order['travel_date']}\n"
                f"🪑 Seat: {order['seat_type']}\n\n"
                f"📌 Order ID: {order['id']}"
        )


async def admin_notification_not_route(order: dict, bot: Bot) -> None:
    # Admin Notification about new order with manual payment
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            "📥 New NOT FOUND route order:\n\n"
            f"👤 @{order['username']}\n"
            f"🛤 {order['departure']} → {order['destination']}\n"
            f"👥 Quantity: {order['quantity']}\n"
            f"🕐 Date: {order['travel_date']}\n"
            f"🪑 Seat: {order['seat_type']}\n\n"
        )
