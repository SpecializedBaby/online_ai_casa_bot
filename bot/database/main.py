import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import inspect, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

from bot.config import config

engine = create_async_engine(url=config.DB_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self, exclude_none: bool = False) -> dict:
        """
        Converts the object of the model into a dictionary.

        Args:
            exclude_none (bool): Will None exclude values ​​from the result

        Returns:
            dict: Dictionary with object data
        """
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            # Converting special data types
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            # Add the value to the result
            if not exclude_none or value is not None:
                result[column.key] = value

        return result
