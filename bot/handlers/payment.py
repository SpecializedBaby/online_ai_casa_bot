from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import broker
from bot.database.dao.dao import BookingDAO, PaymentDAO
from bot.database.schemas.booking import BookingBase, SetPayment
from bot.keyboards.user import general_keyboard_menu, get_keyboard_pay_btn
from bot.database.schemas.payment import PaymentCreate
from bot.services.crypto import create_invoice

from loguru import logger

payment_router = Router()


@payment_router.callback_query(lambda c: c.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, session: AsyncSession, dao: dict):
    booking_dao: BookingDAO = dao["booking"]
    payment_dao: PaymentDAO = dao["payment"]
    user_id = callback.from_user.id

    try:
        # Get latest booking
        last_booking = await booking_dao.find_last_by_user(user_id=user_id)

        if not last_booking:
            await callback.message.answer("❌ No booking found.")
            return

        # Extract payment method
        method = callback.data.removeprefix("pay_")
        payment = await payment_dao.add(PaymentCreate(payment_method=method, invoice_id=None))

        # Update booking with payment reference
        await booking_dao.update(
            filters=BookingBase(id=last_booking.id),
            values=SetPayment(payment_id=payment.id)
        )

        await callback.message.delete()

        # Manual payment flow
        if method == "manual":
            await callback.message.answer(
                "🕐 Please wait for support to contact you.",
                reply_markup=general_keyboard_menu()
            )
            admin_text = (
                "📥 New MANUAL PAYMENT booking:\n\n"
                f"👤 @{callback.from_user.username} ({user_id})\n"
                f"🛤 {last_booking.route.departure} → {last_booking.route.destination}\n"
                f"👥 Quantity: {last_booking.quantity}\n"
                f"💰 Price: {last_booking.price} USDT\n"
                f"🕐 Date: {last_booking.date}\n"
                f"🪑 Seat: {last_booking.seat_type}\n\n"
                f"📌 Booking ID: {last_booking.id}"
            )
            await broker.publish(message=admin_text, queue="admin_msg")
            return

        # Cryptobot payment flow
        if method == "cryptobot":
            invoice = await create_invoice(amount=last_booking.price)
            payment.invoice_id = invoice.invoice_id
            await session.commit()  # store invoice ID for tracking
            await broker.publish(
                message={"booking_id": last_booking.id, "invoice_id": invoice.invoice_id, "user_id": user_id},
                queue="crypto_check",
            )
            await callback.message.answer(
                "✅ Booking confirmed.\n\n💳 Please complete your payment:",
                reply_markup=get_keyboard_pay_btn(invoice=invoice)
            )
            return

        # Unknown method
        await callback.message.answer("⚠️ Unknown payment method selected.")

        logger.info(
            f"User {user_id} started payment process. "
            f"Booking={last_booking.id}, Method={method}, PaymentID={payment.id}"
        )

    except Exception as e:
        logger.error(f"Error in payment process for user {user_id}: {e}")
        await callback.message.answer("⚠️ Something went wrong. Please try again later.")
