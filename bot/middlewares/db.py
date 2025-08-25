from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.database.dao.dao import UserDAO, BookingDAO, PaymentDAO, RouteDAO, OfferDAO, MonthlyPassDAO


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            data["dao"] = {
                "user": UserDAO(session),
                "booking": BookingDAO(session),
                "payment": PaymentDAO(session),
                "route": RouteDAO(session),
                "offer": OfferDAO(session),
                "pass": MonthlyPassDAO(session)
            }
            return await handler(event, data)
