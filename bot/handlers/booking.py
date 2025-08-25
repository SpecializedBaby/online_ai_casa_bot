from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.dao.dao import BookingDAO, RouteDAO
from bot.database.schemas.booking import CreateBooking
from bot.keyboards.user import get_keyboard_seat_classes, get_keyboard_quantity_number, get_keyboard_confirmation, \
    general_keyboard_menu, get_keyboard_payment_method
from bot.states.user import JourneyBooking

booking_router = Router()


class RouteNotFound(Exception): ...


@booking_router.message(Command("booking"))
async def booking_start(message: Message, state: FSMContext):
    await state.set_state(JourneyBooking.departure)
    await message.answer(
        "What is your depart stop from where you are going travel?...",
        reply_markup=ReplyKeyboardRemove()
    )

@booking_router.message(JourneyBooking.departure)
async def process_departure(message: Message, state: FSMContext):
    await state.update_data(departure=message.text)
    await state.set_state(JourneyBooking.destination)
    await message.answer("Where are you going?...")


@booking_router.message(JourneyBooking.destination)
async def process_destination(message: Message, state: FSMContext):
    await state.update_data(destination=message.text)
    await state.set_state(JourneyBooking.travel_date)
    await message.answer("When are you planning traval? (today, tomorrow, 31 Dec ...etc.)")


@booking_router.message(JourneyBooking.travel_date)
async def process_travel_date(message: Message, state: FSMContext):
    await state.update_data(travel_date=message.text)
    await state.set_state(JourneyBooking.seat_type)
    await message.answer(
        "💺 Choose seat type: ",
        reply_markup=get_keyboard_seat_classes())


@booking_router.callback_query(JourneyBooking.seat_type)
async def process_seat_type(callback: CallbackQuery, state: FSMContext):
    await state.update_data(seat_type=callback.data)
    await state.set_state(JourneyBooking.quantity)

    await callback.message.answer(
        "👥 How many tickets would you like to book?",
        reply_markup=get_keyboard_quantity_number()
    )


@booking_router.callback_query(JourneyBooking.quantity)
async def process_quantity(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    dao: dict
):
    """
    Handle quantity selection for a journey booking.
    Validates input, calculates total price, and asks user to confirm.
    If no route store in log.txt, do not save booking.
    """
    user_id = callback.from_user.id
    route_dao: RouteDAO = dao["route"]
    # 1. Validate
    try:
        qty = int(callback.data)
        if qty < 1 or qty > 10:
            raise ValueError
    except (ValueError, TypeError):
        await callback.message.answer("❌ Enter a number between 1 and 10.")
        return

    # 2. Fetch route
    data = await state.get_data()
    try:
        route = await route_dao.get_route(data["departure"], data["destination"])

        if route is None:
            raise RouteNotFound()

        # 3. Calculate total
        total = float(route.cost) * qty
        await state.update_data(quantity=qty, price=total, route_id=route.id)
        data = await state.get_data()

        # 4. Ask user for confirmation
        await callback.message.delete()
        await callback.message.answer(
            "✅ Please confirm your booking:\n\n"
            f"🛤 Route: {data['departure']} → {data['destination']}\n"
            f"📅 Date: {data['travel_date']}\n"
            f"🪑 Seat: {data['seat_type']}\n"
            f"👥 Quantity: {qty}\n"
            f"💰 Total: {total} USDT",
            reply_markup=get_keyboard_confirmation()
        )
        await state.set_state(JourneyBooking.confirmation)
    except RouteNotFound:
        # Feature save routes while not found into BD table not found for CRM
        logger.error(f"Route not found: {data['departure']} -> {data['destination']}")
        await callback.message.answer(
            "❌ Route not found. Request sent to support.",
            reply_markup=general_keyboard_menu()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error processing quantity for user {user_id}: {e}", exc_info=True)
        await callback.message.answer("❌ Something went wrong. Please try again later.")


@booking_router.callback_query(JourneyBooking.confirmation)
async def process_confirm(callback: CallbackQuery, state: FSMContext, session: AsyncSession, dao: dict):
    booking_dao: BookingDAO = dao["booking"]
    user_id = callback.from_user.id
    decision = callback.data

    data = await state.get_data()
    try:
        if decision == "cancel_booking":
            await state.clear()
            await callback.message.delete()
            await callback.message.answer("❌ Order cancelled.", reply_markup=general_keyboard_menu())
            return

        if decision == "confirm_booking":
            booking = CreateBooking(
                user_id=user_id,
                route_id=data["route_id"],
                payment_id=None,
                date=data["travel_date"],
                seat_type=data["seat_type"],
                quantity=data["quantity"],
                price=data["price"],
                status="unpaid",
            )
            await booking_dao.add(booking)

            await callback.message.delete()
            await callback.message.answer(
                "💳 Choose your payment method:",
                reply_markup=get_keyboard_payment_method()
            )
    except Exception as e:
        logger.error(f"Error in process_confirm for user {user_id}: {e}", exc_info=True)
        await callback.message.answer("⚠️ Something went wrong. Please try again later.")
    finally:
        await state.clear()
