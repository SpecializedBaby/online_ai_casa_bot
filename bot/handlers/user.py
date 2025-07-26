import datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command

from bot.handlers.states import TicketOrder
from bot.keyboards.default import get_keyboard_seat_classes, get_keyboard_pay_btn, get_keyboard_quantity_number, \
    get_keyboard_confirmation
from bot.services.crypto import create_invoice
from bot.services.routes import get_route_price
from bot.storage.db import save_order, get_user_orders

order_router = Router()


@order_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(TicketOrder.departure)
    await message.answer(
        "👋 Welcome to Ticket Bot!\n"
        "What is your depart stop from where you are going travel?",
        reply_markup=ReplyKeyboardRemove()
    )

@order_router.message(TicketOrder.departure)
async def process_departure(message: Message, state: FSMContext):
    await state.update_data(departure=message.text)
    await state.set_state(TicketOrder.destination)
    await message.answer("Where are you going?")

@order_router.message(TicketOrder.destination)
async def process_destination(message: Message, state: FSMContext):
    await state.update_data(destination=message.text)
    await state.set_state(TicketOrder.travel_date)
    await message.answer("When are you planning traval?")

@order_router.message(TicketOrder.travel_date)
async def process_travel_date(message: Message, state: FSMContext):
    await state.update_data(travel_date=message.text)
    await state.set_state(TicketOrder.seat_type)
    await message.answer(
        "💺 Choose seat type:",
        reply_markup=get_keyboard_seat_classes())

@order_router.message(TicketOrder.seat_type)
async def process_seat_type(message: Message, state: FSMContext):
    await state.update_data(seat_type=message.text)
    await state.set_state(TicketOrder.quantity)

    await message.answer(
        "👥 How many tickets would you like to book?",
        reply_markup=get_keyboard_quantity_number()
    )

@order_router.message(TicketOrder.quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        qty = int(message.text)
        if qty < 1 or qty > 10:
            raise ValueError
    except Exception as e:
        print(e)  # debug
        await message.answer("❌ Enter a number between 1 and 10.")
        return

    await state.update_data(quantity=qty)
    data = await state.get_data()

    # Calculate total price
    unit_price = get_route_price(departure=data["departure"], destination=data["destination"])
    total = unit_price * qty
    await state.update_data(price=total)

    await message.answer(
        f"Please confirm your booking:\n\n"
        f"🛤 Route: {data['departure']} → {data['destination']}\n"
        f"📅 Date: {data['travel_date']}\n"
        f"🪑 Seat: {data['seat_type']}\n"
        f"👥 Quantity: {qty}\n"
        f"💰 Total: {total} USDT",
        reply_markup=get_keyboard_confirmation()
    )
    await state.set_state(TicketOrder.confirm)


@order_router.callback_query(lambda c: c.data in ["confirm_order", "cancel_order"])
async def process_confirm(callback: CallbackQuery, state: FSMContext):
    # Cancel query process
    if callback.message == "cancel_order":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(f"The order dropped!", reply_markup=ReplyKeyboardRemove())
        return

    # Confirm and pay proces of the order
    # Create invoice
    data = await state.get_data()
    amount = data["price"]
    invoice = await create_invoice(amount=amount)

    #  save and commit the order to DB
    await save_order({
        "user_id": callback.from_user.id,
        "username": callback.from_user.username,
        "departure": data["departure"],
        "destination": data["destination"],
        "travel_date": data["travel_date"],
        "seat_type": data["seat_type"],
        "quantity": data["quantity"],
        "price": data["price"],
        "invoice_id": invoice.invoice_id,
    })

    # Pay process
    await callback.message.answer(
        "✅ Booking confirmed. Please proceed to payment:\n\n",
        reply_markup=get_keyboard_pay_btn(invoice=invoice)
    )

    await state.clear()


@order_router.message(Command("myorders"))
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
