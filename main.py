import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from bot.config import config
from bot.database.main import async_session_maker
from bot.handlers import user, admin, other
from bot.middlewares.db import DbSessionMiddleware
from bot.middlewares.state_clear import StateClearMiddleware

# from bot.tasks import monitor_payments


async def main():
    # Setup bot
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares
    dp.update.middleware(DbSessionMiddleware(session_pool=async_session_maker))
    # Automatically reply to all callbacks
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.message.middleware(StateClearMiddleware())

    # Routes
    dp.include_router(user.user_router)
    dp.include_router(admin.admin_router)
    dp.include_router(other.other_router)

    print("https://t.me/online_ai_casa_bot")

    # Tasker
    # asyncio.create_task(monitor_payments(bot))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
