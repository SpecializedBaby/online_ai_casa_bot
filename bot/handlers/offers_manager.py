from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot.database.dao.dao import OfferDAO
from bot.handlers.admin import admin_required
from bot.states.admin import AddOffer

offers_router = Router()


@offers_router.message(Command("add_offer"))
@admin_required
async def update_offer(message: Message, state: FSMContext):
    await state.set_state(AddOffer.name)
    await message.answer("What is the name  for new offer?", reply_markup=ReplyKeyboardRemove())

@offers_router.message(AddOffer.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddOffer.description)
    await message.answer("What is the description this offer?")

@offers_router.message(AddOffer.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddOffer.advantages)
    await message.answer("What is the advantages this offer?")

@offers_router.message(AddOffer.advantages)
async def process_advantages(message: Message, state: FSMContext):
    await state.update_data(advantages=message.text)
    await state.set_state(AddOffer.url)
    await message.answer("What is the url of the original website this offer?")

@offers_router.message(AddOffer.url)
async def process_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    await state.set_state(AddOffer.price)
    await message.answer("What is the cost this offer?")

@offers_router.message(AddOffer.price)
async def process_price(message: Message, state: FSMContext, dao: dict):
    await state.update_data(price=message.text)
    data = await state.get_data()

    offer_dao: OfferDAO = dao["offer"]

    try:
        result = await offer_dao.create_or_update_offer(**data)
        await message.answer(f"New Offer was {result}")  # Update or Add as new
    except Exception as e:
        logger.error(f"Get error in add_offer method: {e}", exc_info=True)
        await message.answer("❗ Usage: /add_route <departure> <destination> <price>")
    finally:
        await state.clear()
