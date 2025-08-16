from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.keyboards.default import general_keyboard_menu, get_keyboard_payment_method, get_keyboard_pay_btn
from bot.services.crypto import create_invoice
from bot.database.db import get_last_order_by_user_id, update_order_data, get_user_orders

order_router = Router()


@order_router.callback_query(lambda c: c.data in ["confirm_order", "cancel_order"])
async def process_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    decision = callback.data

    last_order = await get_last_order_by_user_id(user_id)
    if not last_order:
        await callback.message.answer("❌ No order found.")
        return

    # Cancel query process
    if decision == "cancel_order":
        await callback.message.delete()
        await callback.message.answer("❌ Order has been cancelled.", reply_markup=general_keyboard_menu())
        await update_order_data(order_id=last_order["id"], status="cancelled")
        return

    # Confirmed
    elif decision == "confirm_order":
        # Get the payment methods
        await callback.message.delete()
        await callback.message.answer(
            "💳 Choose your payment method:",
            reply_markup=get_keyboard_payment_method()
        )

    await callback.answer("Make your choose or call support!")


@order_router.callback_query(lambda c: c.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    last_order = await get_last_order_by_user_id(user_id)
    if not last_order:
        await callback.message.answer("❌ Order not found.")
        return

    await update_order_data(order_id=last_order["id"], payment_method=callback.data)

    await callback.message.delete()

    if callback.data== "pay_manual":
        await callback.message.answer(f"Wait for support answer!", reply_markup=general_keyboard_menu())

    elif callback.data == "pay_cryptobot":
        # Create invoice via cryptobot
        amount = float(last_order["price"])
        invoice = await create_invoice(amount=amount)
        await update_order_data(order_id=last_order["id"], invoice_id=invoice.invoice_id)

        # Pay process
        await callback.message.answer(
            "✅ Booking confirmed. Please proceed to payment:\n\n",
            reply_markup=get_keyboard_pay_btn(invoice=invoice)
        )

@order_router.message(Command("my_orders"))
async def user_order_history(message: Message):
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📭 You have no paid tickets.")
        return

    text = ""
    for i, o in enumerate(orders, 1):
        text += (
            f"🎫 <b>Order #{i}</b>\n"
            f"From: {o['departure']} ➡ {o['destination']}\n"
            f"Date: {o['travel_date']}\n"
            f"Seat: {o['seat_type']}\n"
            f"Tickets: {o['quantity']}\n"
            f"Price: {o['price']} USDT\n\n"
        )

    await message.answer(text)
