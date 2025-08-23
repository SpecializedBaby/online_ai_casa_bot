from contextlib import asynccontextmanager
from aiogram.types import Update
from fastapi import FastAPI, Request
from loguru import logger

from bot.create_bot import dp, start_bot, bot, stop_bot
from bot.config import config, broker, scheduler
from bot.api.router import router as router_fast_stream, disable_booking
from bot.database.main import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("The bot is launched ...")
    await start_bot()
    await broker.start()
    scheduler.start()
    scheduler.add_job(
        disable_booking,
        trigger="interval",
        minutes=30,
        id="disable_booking_task",
        replace_existing=True
    )
    webhook_url = config.hook_url
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    logger.success(f"Webhook is installed:{webhook_url}")
    yield
    logger.info("The bot is stopped ...")
    await stop_bot()
    await broker.close()
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook(request: Request) -> None:
    logger.info("A request from webhook was received.")
    try:
        update_data = await request.json()
        update = Update.model_validate(update_data, context={"bot": bot})
        await dp.feed_update(bot, update)
        logger.info("The update is successfully processed.")
    except Exception as e:
        logger.error(f"Error when processing update with webhook: {e}")


app.include_router(router_fast_stream)
