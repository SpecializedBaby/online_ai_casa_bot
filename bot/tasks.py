import asyncio
import datetime

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.database.dao.dao import BookingDAO
from bot.database.schemas.booking import BookingByStatus
from bot.keyboards.user import general_keyboard_menu
from bot.services.crypto import get_invoice_status

ADMIN_IDS = config.ADMIN_IDS


async def monitor_payments(bot: Bot, session: AsyncSession, dao: dict):
    """
    Periodically check unpaid orders, handle payments, notify users/admins,
    and cancel expired bookings.
    """
    booking_dao = BookingDAO(session)

    while True:
        try:
            unpaid_orders = await booking_dao.find_all(filters=BookingByStatus(status="unpaid"))
            time_now = datetime.datetime.utcnow()

            for order in unpaid_orders:
                try:
                    # --- Cryptobot payment flow ---
                    if order["payment_method"] == "pay_cryptobot":
                        status = await get_invoice_status(order["invoice_id"])
                        if status == "paid":
                            await user_notification_paid_order(user_id=order["user_id"], bot=bot)
                            await mark_order_paid(order["id"])
                            await admin_notification_paid_order(order=order, bot=bot)
                            await mark_notified_admin(order["id"])
                            continue

                    # --- Manual payment flow ---
                    elif order["payment_method"] == "pay_manual" and not order["notified"]:
                        await admin_notification_manual_order(order=order, bot=bot)
                        await mark_notified_admin(order["id"])

                    # --- Orders without a matching route ---
                    elif not order["notified"] and order.get("price") is None:
                        await admin_notification_not_route(order=order, bot=bot)
                        await mark_notified_admin(order["id"])

                    # --- Expiration check ---
                    created_time = datetime.datetime.strptime(order["created_time"], "%Y-%m-%d %H:%M:%S")
                    if (time_now - created_time).total_seconds() > 3600:  # 60 minutes
                        await mark_order_canceled(order["id"])
                        try:
                            await bot.send_message(
                                order["user_id"],
                                "⌛ Your booking was canceled due to unpaid status after 60 minutes."
                            )
                        except Exception as e:
                            logger.warning(f"Failed to notify user {order['user_id']} about cancellation: {e}")

                except Exception as e:
                    logger.error(f"Error processing order {order.get('id')}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error in monitor_payments loop: {e}", exc_info=True)

        await asyncio.sleep(30)  # run every 30s


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
