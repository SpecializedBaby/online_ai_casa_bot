from datetime import datetime
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from bot.database.models import User, Route, Payment, Booking
from bot.database.dao.base import BaseDAO
from bot.database.schemas.booking import BookingBase, BookingByStatus, BookingsByUser


class UserDAO(BaseDAO[User]):
    model = User


class RouteDAO(BaseDAO[Route]):
    model = Route


class PaymentDAO(BaseDAO[Payment]):
    model = Payment


class BookingDAO(BaseDAO[Booking]):
    model = Booking

    async def get_booking_paid(self, user_id: int) -> list[Booking]:
        logger.info(f"Get paid booking by User_ID: {user_id}")
        try:
            result = await self.find_all(
                BookingsByUser(user_id=user_id, status="paid")
            )
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error fetching last booking for user {user_id}: {e}")
            raise



    async def find_last_by_user(self, user_id: int) -> Booking | None:
        logger.info(f"Get last booking by User_ID: {user_id}")
        try:
            query = select(self.model).order_by(self.model.id.desc()).limit(1)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Record the last booking of user_id:{user_id} {'found' if record else 'not found'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Error fetching last booking for user {user_id}: {e}")
            raise

    async def cancel_expired_books(self):
        try:
            exp_time = datetime.utcnow() - timedelta(minutes=60)

            query = (
                select(self.model)
                .filter_by(status="unpaid")
                .where(self.model.created_at < exp_time)
                .values(status="canceled")
                .execution_options(synchronize_session="fetch")
            )
            result = await self._session.execute(query)
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Error when canceling the expired books: {e}")
            await self._session.rollback()
            raise

    async def delete_book(self, book_id: int):
        try:
            result = await self.delete(filters=BookingBase(id=book_id))
            logger.info(f"Deleted {result.rowcount} records.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Error when removing records: {e}")
            await self._session.rollback()
            raise

    async def mark_paid(self, book_id: int):
        try:
            result = await self.update(
                filters=BookingBase(id=book_id),
                values=BookingByStatus(status="paid")
            )
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Error when canceling a book with ID {book_id}: {e}")
            await self._session.rollback()
            raise

    async def mark_cancel(self, book_id: int):
        try:
            result = await self.update(filters=BookingBase(id=book_id), values=BookingByStatus(status="canceled"))
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Error when canceling a book with ID {book_id}: {e}")
            await self._session.rollback()
            raise
