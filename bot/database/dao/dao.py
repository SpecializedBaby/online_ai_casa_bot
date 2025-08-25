from datetime import datetime
from loguru import logger
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from bot.database.models import User, Route, Payment, Booking, Offer, MonthlyPass
from bot.database.dao.base import BaseDAO
from bot.database.schemas.booking import BookingBase, BookingByStatus, BookingsByUser
from bot.database.schemas.route import RouteFind, RouteCostUpdate
from bot.database.schemas.offers import OfferName, OffersCreate, OffersBase
from bot.database.schemas.monthly_pass import PassCreate
from bot.database.schemas.user import UserUpdate, UserBase


class OfferDAO(BaseDAO[Offer]):
    model = Offer

    async def create_or_update_offer(self, data: dict) -> str:
        try:
            offer_obj = OffersCreate(**data)

            offer = await self.find_one_or_none(
                filters=OfferName(name=offer_obj.name)
            )

            if offer:
                await self.update(
                    filters=OffersBase(id=offer.id),
                    values=offer_obj
                )
                return "update"

            await self.add(offer_obj)
            return "Create"
        except ValidationError as e:
            logger.error(f"Pydantic error in create_or_update_offer: {e}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"DB error in create_or_update_offer: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_or_update_offer: {e}", exc_info=True)
            raise


class MonthlyPassDAO(BaseDAO[MonthlyPass]):
    model = MonthlyPass

    async def add_order(self, data: dict):
        try:
            order = await self.add(PassCreate(
                user_id=data["user_id"],
                payment_id=None,
                offer_id=data["offer_id"],
                month=data["month"]
            ))
            return order
        except ValidationError as e:
            logger.error(f"Pydantic error in create_or_update_offer: {e}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"DB error in create_or_update_offer: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_or_update_offer: {e}", exc_info=True)
            raise


class UserDAO(BaseDAO[User]):
    model = User

    async def update_details(self, user_id: int, data: dict):
        try:
            result = await self.update(
                filters=UserBase(id=user_id),
                values=UserUpdate(
                    username=data.get("username", None),
                    full_name=data["full_name"],
                    age=data["age"],
                    zip_code=data["zip_code"]
                )
            )
            return result
        except ValidationError as e:
            logger.error(f"Pydantic error in update_details: {e}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"DB error in update_details: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in update_details: {e}", exc_info=True)
            raise


class RouteDAO(BaseDAO[Route]):
    model = Route

    async def get_route(self, departure: str, destination: str) -> Route:
        try:
            result = await self.find_one_or_none(
                filters=RouteFind(
                    departure=departure,
                    destination=destination
                )
            )
            return result
        except ValidationError as e:
            logger.error(f"Pydantic error in get_route by names: {departure} -> {destination}: {e}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"DB Error fetching route by names {departure} -> {destination}: {e}", exc_info=True)
            raise

    async def update_cost(self, dep: str, dest: str, cost: float):
        try:
            result = await self.update(
                filters=RouteFind(departure=dep, destination=dest),
                values=RouteCostUpdate(cost=cost)
            )
            return result
        except ValidationError as e:
            logger.error(f"Pydantic error in update_cost by names: {dep} -> {dest}: {e}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error update route cost({cost}) by names {dep} -> {dest}: {e}")
            raise


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
        except ValidationError as e:
            logger.error(f"Pydantic error in get_booking_paid by user_id: {user_id}: {e}", exc_info=True)
            raise
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


    async def delete_book(self, book_id: int):
        try:
            result = await self.delete(filters=BookingBase(id=book_id))
            logger.info(f"Deleted {result.rowcount} records.")
            await self._session.flush()
            return result.rowcount
        except ValidationError as e:
            logger.error(f"Pydantic error in delete_book by book_id: {book_id}: {e}", exc_info=True)
            raise
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
        except ValidationError as e:
            logger.error(f"Pydantic error in mark_paid by book_id: {book_id}: {e}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error when canceling a book with ID {book_id}: {e}")
            await self._session.rollback()
            raise

    async def mark_cancel(self, book_id: int):
        try:
            result = await self.update(
                filters=BookingBase(id=book_id),
                values=BookingByStatus(status="canceled")
            )
            await self._session.flush()
            return result.rowcount
        except ValidationError as e:
            logger.error(f"Pydantic error in mark_cancel by book_id: {book_id}: {e}", exc_info=True)
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error when canceling a book with ID {book_id}: {e}")
            await self._session.rollback()
            raise
