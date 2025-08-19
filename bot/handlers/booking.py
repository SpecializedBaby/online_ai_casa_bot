from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.filters import Command
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.dao.dao import BookingDAO, RouteDAO
from bot.database.schemas.booking import BookingsByUser, CreateBooking, BookingBase, BookingByStatus
from bot.database.schemas.route import GetRoute
from bot.keyboards.user import get_keyboard_seat_classes, get_keyboard_quantity_number, get_keyboard_confirmation, \
    general_keyboard_menu, get_keyboard_payment_method
from bot.states.user import JourneyBooking

booking_router = Router()


@booking_router.callback_query(lambda c: c.data in ["confirm_booking", "cancel_booking"])
async def process_confirm(callback: CallbackQuery, session: AsyncSession, dao: dict):
    booking_dao: BookingDAO = dao["booking"]
    user_id = callback.from_user.id
    decision = callback.data

    try:
        # Get last booking for this user
        last_booking = await booking_dao.find_last_by_user(user_id=user_id)

        if not last_booking:
            await callback.message.answer("❌ No order found.")
            return

        # Cancel booking
        if decision == "cancel_booking":
            await booking_dao.update(
                filters=BookingBase(id=last_booking.id),
                values=BookingByStatus(status="cancelled")
            )
            await callback.message.delete()
            await callback.message.answer(
                "❌ Order has been cancelled.",
                reply_markup=general_keyboard_menu()
            )
            return

        # Confirm booking → move to payment
        if decision == "confirm_booking":
            await booking_dao.update(
                filters=BookingBase(id=last_booking.id),
                values=BookingByStatus(status="pending")
            )
            await callback.message.delete()
            await callback.message.answer(
                "💳 Choose your payment method:",
                reply_markup=get_keyboard_payment_method()
            )

        await callback.answer("✅ Done! Continue with your choice.")

    except Exception as e:
        logger.error(f"Error in process_confirm for user {user_id}: {e}")
        await callback.message.answer("⚠️ Something went wrong. Please try again later.")


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
    Validates input, calculates total price, creates booking, and asks for confirmation.
    """
    user_id = callback.from_user.id
    booking_dao: BookingDAO = dao["booking"]
    route_dao: RouteDAO = dao["route"]
    data = await state.get_data()
    booking = CreateBooking(
        user_id=user_id,
        route_id=None,
        payment_id=None,
        date=data["travel_date"],
        seat_type=data["seat_type"],
        quantity=None,
        price=None,
        status="unpaid"
    )

    # 1 Validate quantity
    try:
        qty = int(callback.data)
        if qty < 1 or qty > 10:
            raise ValueError
    except Exception as e:
        logger.warning(f"Invalid quantity '{callback.data}' from user {user_id}: {e}")
        await callback.message.answer("❌ Enter a number between 1 and 10.")
        return
    else:
        # Save in Schema quantity field
        booking.quantity = qty

    try:
        # 3 Fetch route
        route = await route_dao.find_one_or_none(
            filters=GetRoute(
                departure=data["departure"],
                destination=data["destination"]
            )
        )
        if not route:
            # Save booking like MANUAL
            booking.status = "manual"
            raise LookupError("Route not found")
        # Save route in Schema
        booking.route_id = route.id

        # 4 Calculate total and save booking
        total = float(route.cost) * qty
        await state.update_data(quantity=qty, price=total)
        await callback.message.delete()

        # Save Schema with status CONFIRMATION
        booking.price = total
        booking.status = "confirming"

        # 5 Ask user for confirmation
        await callback.message.answer(
            "✅ Please confirm your booking:\n\n"
            f"🛤 Route: {data['departure']} → {data['destination']}\n"
            f"📅 Date: {data['travel_date']}\n"
            f"🪑 Seat: {data['seat_type']}\n"
            f"👥 Quantity: {qty}\n"
            f"💰 Total: {total} USDT",
            reply_markup=get_keyboard_confirmation()
        )

    except LookupError:
        # Save fallback booking if route is missing
        logger.error(f"Route not found for booking request: {data} by user {user_id}")
        await callback.message.answer(
            "❌ We couldn't find this route.\n"
            "📩 Your request has been sent to support. Please wait for a reply.",
            reply_markup=general_keyboard_menu()
        )
    except Exception as e:
        logger.error(f"Error processing quantity for user {user_id}: {e}", exc_info=True)
        await callback.message.answer("❌ Something went wrong. Please try again later.")
    finally:
        # 6 save data and Clear FSM state regardless of outcome
        await booking_dao.add(booking)
        await state.clear()
