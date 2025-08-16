from datetime import date, datetime
from typing import Dict
from loguru import logger
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

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
