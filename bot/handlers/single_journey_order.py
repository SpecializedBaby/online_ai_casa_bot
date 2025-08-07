from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.config import get_config
from bot.handlers.states import JourneyOrder
from bot.keyboards.default import get_keyboard_seat_classes, get_keyboard_quantity_number, general_keyboard_menu, \
    get_keyboard_confirmation
from bot.services.routes import get_route_price
from bot.storage.db import save_order

journey_router = Router()

config = get_config()


@journey_router.message(Command("book"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(JourneyOrder.departure)
    await message.answer(
        "What is your depart stop from where you are going travel?...",
        reply_markup=ReplyKeyboardRemove()
    )


@journey_router.message(JourneyOrder.departure)
async def process_departure(message: Message, state: FSMContext):
    await state.update_data(departure=message.text)
    await state.set_state(JourneyOrder.destination)
    await message.answer("Where are you going?...")


@journey_router.message(JourneyOrder.destination)
async def process_destination(message: Message, state: FSMContext):
    await state.update_data(destination=message.text)
    await state.set_state(JourneyOrder.travel_date)
    await message.answer("When are you planning traval? (today, tomorrow, 31 Dec ...etc.)")


@journey_router.message(JourneyOrder.travel_date)
async def process_travel_date(message: Message, state: FSMContext):
    await state.update_data(travel_date=message.text)
    await state.set_state(JourneyOrder.seat_type)
    await message.answer(
        "💺 Choose seat type: ",
        reply_markup=get_keyboard_seat_classes())


@journey_router.callback_query(JourneyOrder.seat_type)
async def process_seat_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(seat_type=callback.data)
    await state.set_state(JourneyOrder.quantity)

    await callback.message.answer(
        "👥 How many tickets would you like to book?",
        reply_markup=get_keyboard_quantity_number()
    )


@journey_router.callback_query(JourneyOrder.quantity)
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
        unit_price = await get_route_price(
            departure=data["departure"],
            destination=data["destination"]
        )
        if unit_price is None:
            raise ValueError
        total = float(unit_price) * qty
        await state.update_data(price=total)
        await callback.message.delete()
        # Save confirmed order with calculated total price
        await save_order({
            "user_id": callback.from_user.id,
            "username": callback.from_user.username,
            "departure": data["departure"],
            "destination": data["destination"],
            "travel_date": data["travel_date"],
            "seat_type": data["seat_type"],
            "quantity": qty,
            "price": total,
            "payment_method": None,  # Set later via confirm step
            "invoice_id": None,
            "status": "waiting_confirm"  # Track status
        })
        await callback.message.answer(
            f"Please confirm your booking:\n\n"
            f"🛤 Route: {data['departure']} → {data['destination']}\n"
            f"📅 Date: {data['travel_date']}\n"
            f"🪑 Seat: {data['seat_type']}\n"
            f"👥 Quantity: {qty}\n"
            f"💰 Total: {total} USDT",
            reply_markup=get_keyboard_confirmation()
        )

    except Exception as e:
        # Routes didn't find and save as manual process
        await save_order({
            "user_id": callback.from_user.id,
            "username": callback.from_user.username,
            "departure": data["departure"],
            "destination": data["destination"],
            "travel_date": data["travel_date"],
            "seat_type": data["seat_type"],
            "quantity": qty,
            "price": None,
            "payment_method": "pay_manual",
            "invoice_id": None,
            "status": "manual_pending"
        })

        await callback.message.answer(
            "❌ We couldn't find this route.\n"
            "📩 Your request has been sent to our support team. Please wait for a reply.",
            reply_markup=general_keyboard_menu()
        )
    finally:
        await state.clear()
