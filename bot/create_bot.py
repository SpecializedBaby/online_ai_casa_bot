from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from bot.config import config
from bot.database.main import async_session_maker
from bot.handlers import user, admin, other, booking, payment, offers_manager, offers_ordering
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.state_clear import StateClearMiddleware

from loguru import logger

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


async def start_bot():
    # Middlewares
    dp.update.middleware.register(DbSessionMiddleware(session_pool=async_session_maker))
    dp.message.middleware(StateClearMiddleware())
    # Automatically reply to all callbacks
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    # Routers
    dp.include_router(user.user_router)
    dp.include_router(admin.admin_router)
    dp.include_router(other.other_router)
    dp.include_router(booking.booking_router)
    dp.include_router(payment.payment_router)
    dp.include_router(offers_manager.offers_router)
    dp.include_router(offers_ordering.order_offers)

    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f'I am launched🥳.')
        except:
            pass
    logger.info("The bot has been launched successfully.")


async def stop_bot():
    try:
        for admin_id in config.ADMIN_IDS:
            await bot.send_message(admin_id, 'The bot is stopped. For what? 😔')
    except:
        pass
    logger.error("The bot is stopped!")
