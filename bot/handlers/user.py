import datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from bot.handlers.states import TicketOrder
from bot.keyboards.default import get_keyboard_seat_classes, get_keyboard_pay_btn
from bot.services.crypto import create_invoice
from bot.services.routes import get_route_price
from bot.storage.db import save_order

order_router = Router()


@order_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(TicketOrder.departure)
    await message.answer("👋 Welcome to Ticket Bot!\nWhat is your depart stop from where you are going travel?")

@order_router.message(TicketOrder.departure)
async def process_departure(message: Message, state: FSMContext):
    await state.update_data(departure=message.text)
    await state.set_state(TicketOrder.destination)
    await message.answer("Where are you going?")

@order_router.message(TicketOrder.destination)
async def process_destination(message: Message, state: FSMContext):
    await state.update_data(destination=message.text)
    await state.set_state(TicketOrder.travel_date)
    await message.answer("When are you planning traval? (YYYY-MM-DD):")

@order_router.message(TicketOrder.travel_date)
async def process_travel_date(message: Message, state: FSMContext):
    await state.update_data(travel_date=message.text)
    await state.set_state(TicketOrder.seat_type)
    await message.answer("💺 Choose seat type:", reply_markup=get_keyboard_seat_classes())

@order_router.message(TicketOrder.seat_type)
async def process_seat_type(message: Message, state: FSMContext):
    await state.update_data(seat_type=message.text)
    await state.set_state(TicketOrder.confirm)
    data = await state.get_data()
    summary = (
        f"🔖 <b>Your Ticket:</b>\n"
        f"From: <b>{data['departure']}</b>\n"
        f"To: <b>{data['destination']}</b>\n"
        f"Date: <b>{data['travel_date']}</b>\n"
        f"Seat: <b>{data['seat_type']}</b>\n\n"
        f"✅ Send any message to confirm or /cancel to abort."
    )
    await message.answer(summary, reply_markup=ReplyKeyboardRemove())


@order_router.message(TicketOrder.confirm)
async def process_confirm(message: Message, state: FSMContext):
    data = await state.get_data()

    # for example amount
    price = get_route_price(departure=data["departure"], destination=data["destination"])
    data["price"] = price

    invoice = await create_invoice(amount=price)

    #  set order
    order = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "invoice_url": invoice.bot_invoice_url,
        "invoice_id": invoice.invoice_id,
        "create_date": datetime.datetime.utcnow(),
        **data,
    }

    #  save order
    await save_order(order)

    await message.answer(
        f"🎟 Ticket Confirmed!\n"
        f"<b>From:</b> {data['departure']} ➡ <b>{data['destination']}</b>\n"
        f"<b>Date:</b> {data['travel_date']}\n"
        f"<b>Seat:</b> {data['seat_type']}\n"
        f"<b>Price:</b> <code>{price} USDT</code>\n\n"
        f"👇 Click below to pay with CryptoBot:",
        reply_markup=get_keyboard_pay_btn(invoice=invoice)
    )

    await state.clear()
