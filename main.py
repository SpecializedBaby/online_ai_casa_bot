import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import get_config
from bot.handlers import user, admin, single_journey
from bot.middlewares.state_clear import StateClearMiddleware
from bot.storage.db import init_db
from bot.tasks import monitor_payments


async def main():
    # init database orders.db
    await init_db()

    # Setup bot
    config = get_config()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Routes
    dp.include_router(single_journey.journey_router)
    dp.include_router(user.order_router)
    dp.include_router(admin.admin_router)

    # Middlewares
    dp.message.middleware(StateClearMiddleware())

    print("Bot is starting... !")
    print("https://t.me/online_ai_casa_bot")

    # Tasker
    asyncio.create_task(monitor_payments(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
