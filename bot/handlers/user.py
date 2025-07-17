from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from bot.handlers.states import TicketOrder
from bot.keyboards.default import get_keyboard_seat_classes

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
    await state.clear()
    await message.answer("🎟 Your order has been confirmed! (We'll add payment next 👇)")
