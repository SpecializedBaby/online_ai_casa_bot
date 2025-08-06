import random

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import CommandStart, Command

from bot.config import get_config
from bot.handlers.states import TicketOrder
from bot.keyboards.default import get_keyboard_seat_classes, get_keyboard_pay_btn, get_keyboard_quantity_number, \
    get_keyboard_confirmation, general_keyboard_menu, get_keyboard_payment_method
from bot.services.crypto import create_invoice
from bot.services.routes import get_route_price
from bot.storage.db import save_order, get_user_orders

order_router = Router()

config = get_config()


@order_router.message(CommandStart())
async def welcome_massage(message: Message, state: FSMContext) -> None:
    await message.answer(
        "👋 Welcome to Ticket Bot!",
        reply_markup=general_keyboard_menu()
    )


@order_router.message(Command("book"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(TicketOrder.departure)
    await message.answer(
        "What is your depart stop from where you are going travel?",
        reply_markup=general_keyboard_menu()
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

@order_router.callback_query(TicketOrder.seat_type)
async def process_seat_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(seat_type=callback.data)
    await state.set_state(TicketOrder.quantity)

    await callback.message.answer(
        "👥 How many tickets would you like to book?",
        reply_markup=get_keyboard_quantity_number()
    )

@order_router.callback_query(TicketOrder.quantity)
async def process_quantity(callback: CallbackQuery, state: FSMContext):
    try:
        qty = int(callback.data)
        if qty < 1 or qty > 10:
            raise ValueError
    except Exception as e:
        print(e)  # debug

        await callback.message.answer("❌ Enter a number between 1 and 10.")
        return

    await state.update_data(quantity=qty)
    data = await state.get_data()

    # Calculate total price and get from DB
    try:
        unit_price = await get_route_price(departure=data["departure"], destination=data["destination"])
        if unit_price is None:
            raise ValueError
        total = float(unit_price) * qty
    except Exception as e:
        print(e)  # debug
        await callback.message.answer("❌ We didn't found this route.")
        return

    await state.update_data(price=total)

    await callback.message.answer(
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
        await callback.message.answer(f"The order dropped!", reply_markup=general_keyboard_menu())
        return

    # Confirmed order and got to payment process
    await callback.message.answer(
        "✅ Booking confirmed. Please proceed to payment:\n\n",
        reply_markup=get_keyboard_payment_method()
    )
    await state.set_state(TicketOrder.payment)


@order_router.callback_query(lambda c: c.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data["price"]

    if callback.message == "pay_manual":
        await callback.message.delete()
        await save_order({
            "user_id": callback.from_user.id,
            "username": callback.from_user.username,
            "departure": data["departure"],
            "destination": data["destination"],
            "travel_date": data["travel_date"],
            "seat_type": data["seat_type"],
            "quantity": data["quantity"],
            "price": data["price"],
            "payment_method": data["payment"],
            "invoice_id": random.randint(a=1, b=999999),
        })
        await callback.message.answer(f"Wait for support answer!", reply_markup=general_keyboard_menu())

    elif callback.message == "pay_cryptobot":
        # Create invoice via cryptobot
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
            "payment_method": data["payment"],
            "invoice_id": invoice.invoice_id,
        })

        # Pay process
        await callback.message.answer(
            "✅ Booking confirmed. Please proceed to payment:\n\n",
            reply_markup=get_keyboard_pay_btn(invoice=invoice)
        )

    await state.clear()


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

@order_router.message(Command("help"))
async def get_help(message: Message):
    supports = "\n".join(config.supports)

    await message.answer(
        f"ALl supports here:\n{supports}"
    )
