from datetime import datetime, timedelta
from faststream.rabbit.fastapi import RabbitRouter
from loguru import logger
from bot.create_bot import bot
from bot.config import config, scheduler, broker
from bot.database.dao.dao import BookingDAO
from bot.database.main import async_session_maker
from bot.services.crypto import get_invoice_status

router = RabbitRouter(url=config.rabbitmq_url)


# Manual command for expire_check (RabbitMQ)
@router.subscriber("expire_check")
async def schedule_expiration():
    scheduler.add_job(
        disable_booking,
        "date",
        run_date=datetime.utcnow() + timedelta(minutes=30),
        id="disable_expired_bookings",
        replace_existing=True,
    )


@router.subscriber("crypto_check")
async def monitor_crypto_payment(data: dict):
    booking_id = data["booking_id"]
    invoice_id = data["invoice_id"]
    user_id = data["user_id"]

    # Checking the crypto payment status in 30sec (APSheduler)
    scheduler.add_job(
        check_invoice_status,
        "interval",
        seconds=30,
        args=[booking_id, invoice_id, user_id],
        id=f"crypto_check_{booking_id}",
        replace_existing=True,
    )


@router.subscriber("admin_msg")
async def send_booking_msg(msg: str):
    for admin in config.ADMIN_IDS:
        await bot.send_message(admin, text=msg)


@router.subscriber("noti_user")
async def schedule_user_notifications(user_id: int):
    """Plans to send a series of messages to the user with different intervals."""
    now = datetime.now()

    notifications = [
        {
            "time": now + timedelta(hours=1),
            "text": "Thanks for the choice of our casa bot! We hope you will like it."
                    "Leave a review so that we become better!",
        },
        {
            "time": now + timedelta(hours=3),
            "text": "Do you need to book the ticket again? Try our new routes!",
        },
    ]

    for i, notification in enumerate(notifications):
        scheduler.add_job(
            send_user_msg,
            "date",
            run_date=notification["time"],
            args=(user_id, notification["text"]),
            id=f"user_notification_{user_id}_{i}",
            replace_existing=True,
        )
        logger.info(
            f"Notification for the user is planned {user_id} on {notification['time']}"
        )


async def disable_booking():
    async with async_session_maker() as session:
        await BookingDAO(session).cancel_expired_books()


async def check_invoice_status(booking_id: int, invoice_id: int, user_id: int):
    status = await get_invoice_status(invoice_id)
    async with async_session_maker() as session:
        booking_dao = BookingDAO(session)

        if status == "paid":
            await booking_dao.mark_paid(booking_id)
            await send_user_msg(user_id, "✅ Your payment is confirmed!")
            await broker.publish(message=f"📬 Paid booking {booking_id}", queue="admin_msg")
            scheduler.remove_job(f"crypto_check_{booking_id}")
        else:
            booking = await booking_dao.find_one_or_none_by_id(data_id=booking_id)
            if (datetime.utcnow() - booking.created_at).total_seconds() > 1800:  # 30 мин
                await booking_dao.mark_cancel(booking_id)
                await send_user_msg(user_id, "⌛ Booking canceled due to timeout.")
                scheduler.remove_job(f"crypto_check_{booking_id}")


async def send_user_msg(user_id: int, text: str):
    await bot.send_message(user_id, text=text)
