import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import get_config
from bot.handlers import user, admin
from bot.services.crypto import get_invoice_status
from bot.storage.db import get_unpaid_orders, mark_order_paid, init_db


async def monitor_payments(bot: Bot):
    while True:
        unpaid_orders = await get_unpaid_orders()
        for order in unpaid_orders:
            status = await get_invoice_status(order["invoice_id"])
            if status == "paid":
                await bot.send_message(order["user_id"], "✅ Payment received. Your ticket is confirmed!")
                await mark_order_paid(order["id"])
        await asyncio.sleep(30)  # check every 30 seconds


async def main():
    # init database orders.db
    await init_db()

    config = get_config()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(user.order_router)
    dp.include_router(admin.admin_router)

    print("Bot is starting... !")
    print("https://t.me/online_ai_casa_bot")

    asyncio.create_task(monitor_payments(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
