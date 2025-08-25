from aiogram import Router
from aiogram.exceptions import AiogramError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from bot.keyboards.offers_kb import get_list_offers, get_months_keyboard
from bot.keyboards.user import general_keyboard_menu, get_keyboard_confirmation, get_keyboard_payment_method
from bot.states.user import OfferOrder
from bot.database.dao.dao import OfferDAO, MonthlyPassDAO, UserDAO

order_offers = Router()

# "offer": RegionalOfferDAO(session),
# "pass": MonthlyPassDAO(session)
# offer_{offer.id}

@order_offers.message(Command("order_offers"))
async def start_order(message: Message, state: FSMContext, dao: dict):
    await state.set_state(OfferOrder.user_id)
    await state.update_data(user_id=message.from_user.id)
    offer_dao: OfferDAO = dao["offer"]

    try:
        offers = await offer_dao.find_all()
        if not offers:
            await message.answer("❌ No offers available at the moment.")
            return
        await message.answer("Opening order chat!", reply_markup=ReplyKeyboardRemove())
        await message.answer(
            "📋 Available offers:",
            reply_markup=get_list_offers(offers)
        )
        await state.set_state(OfferOrder.offer_id)
    except AiogramError as e:
        await message.answer(
            "❌ Invalid format. Use Keyboard please",
            reply_markup=general_keyboard_menu()
        )
        await state.clear()


@order_offers.callback_query(OfferOrder.offer_id)
async def process_offer(callback: CallbackQuery, state: FSMContext, dao: dict):
    offer_id = int(callback.data.split("_")[1])
    await state.update_data(offer_id=offer_id)
    await state.set_state(OfferOrder.full_name)
    await callback.message.answer(
        "🎂 Please enter your fullname (Telegram Bot):"
    )

@order_offers.message(OfferOrder.full_name)
async def process_fullname(message: Message, state: FSMContext, dao: dict):
    await state.update_data(full_name=message.text)
    await state.set_state(OfferOrder.age)
    await message.answer("How old are you? (age in number)")

@order_offers.message(OfferOrder.age)
async def process_age(message: Message, state: FSMContext):
    try:
        await state.update_data(age=int(message.text.strip()))
        await state.set_state(OfferOrder.zip_code)
        await message.answer("Enter a zip/post code of your address!",)
    except TypeError as e:
        await message.answer("Enter a valid number")

@order_offers.message(OfferOrder.zip_code)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(zip_code=message.text.strip())
    await state.set_state(OfferOrder.month)
    await message.answer(
        "📅 Enter the number of months you want the pass for (1–12):",
        reply_markup=get_months_keyboard()
    )

@order_offers.callback_query(OfferOrder.month)
async def process_month(callback: CallbackQuery, state: FSMContext):
    try:
        month = int(callback.data.strip())
        if not (1 <= month <= 12):
            raise ValueError
    except (ValueError, TypeError):
        await callback.message.answer("❌ Enter a number between 1 and 12.")
        return

    await state.update_data(month=month)
    data = await state.get_data()

    # Ask for confirmation
    await callback.message.answer(
        "✅ Please confirm your Offer order:\n\n"
        f"🎂 Age: {data['age']}\n"
        f"🏠 Post_code: {data['zip_code']}\n"
        f"📅 Month: {data['month']}",
        reply_markup=get_keyboard_confirmation()
    )
    await state.set_state(OfferOrder.confirmation)


@order_offers.callback_query(OfferOrder.confirmation)
async def process_confirm(callback: CallbackQuery, state: FSMContext, dao: dict):
    data = await state.get_data()
    user_dao: UserDAO = dao["user"]
    pass_dao: MonthlyPassDAO = dao["pass"]
    user_id = callback.from_user.id

    try:
        if callback.data == "cancel_booking":
            await state.clear()
            await callback.message.answer("❌ Pass order cancelled.")
            return

        if callback.data == "confirm_booking":
            # send payment
            await user_dao.update_details(user_id, data)
            await pass_dao.add_order(data)
            await callback.message.delete()
            await callback.message.answer(
                "🎫 Your offer order has been created!",
                reply_markup=get_keyboard_payment_method()
            )

    except Exception as e:
        logger.error(f"Error saving Pass for {user_id}: {e}", exc_info=True)
        await callback.message.answer("⚠️ Something went wrong. Try again later.")
    finally:
        await state.clear()
