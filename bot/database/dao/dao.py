from typing import Optional
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from bot.database.models import User, Route, Payment, Booking
from bot.database.dao.base import BaseDAO


class UserDAO(BaseDAO[User]):
    model = User


class RouteDAO(BaseDAO[Route]):
    model = Route


class PaymentDAO(BaseDAO[Payment]):
    model = Payment


class BookingDAO(BaseDAO[Booking]):
    model = Booking

    async def find_last_by_user(self, user_id: int) -> Optional[T]:
        logger.info(f"Get last booking by User_ID: {user_id}")
        try:
            query = select(self.model).order_by(self.model.id.desc()).first()
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Record the last booking of user_id:{user_id} {'found' if record else 'not found'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Error fetching last booking for user {user_id}: {e}")
            raise
