from typing import List, TypeVar, Generic, Type, Optional

from pydantic import BaseModel
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from bot.database.main import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self._session = session
        if self.model is None:
            raise ValueError("The model should be indicated in the subsidiary")

    async def find_one_or_none_by_id(self, data_id: int) -> Optional[T]:
        logger.info(f"Get {self.model.__name__} by ID: {data_id}")
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Record {self.model.__name__} with ID {data_id} {'found' if record else 'not found'}."
            logger.info(log_message)
            return record
        except SQLAlchemyError as e:
            logger.error(f"Error when looking for a record with ID {data_id}: {e}")
            raise

    async def find_one_or_none(self, filters: BaseModel) -> Optional[T]:
        # Search by filter
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Search a row from {self.model.__name__} by filters: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Searched: {filter_dict}")
            else:
                logger.info(f"Didn't search: {filter_dict}")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Error with filters {filter_dict}: {e}")
            raise

    async def find_all(self, filters: BaseModel | None = None) -> List[T]:
        try:
            if filters:
                filter_dict = filters.model_dump(exclude_unset=True)
                logger.info(f"Search all rows {self.model.__name__} by filters: {filter_dict}")
                query = select(self.model).filter_by(**filter_dict)
            else:
                logger.info(f"Search all rows {self.model.__name__} without filters")
                query = select(self.model)

            result = await self._session.execute(query)
            records = result.scalars().all()
            logger.info(f"Found {len(records)}.")
            return records
        except SQLAlchemyError as e:
            logger.error(f"Error in find_all method: {e}")
            raise

    async def add(self, data: BaseModel) -> Optional[T]:
        data_dict = data.model_dump(exclude_unset=True)
        logger.info(f"Add data to {self.model.__name__} table: {data_dict}")
        new_instance = self.model(**data_dict)
        self._session.add(new_instance)
        try:
            await self._session.commit()
            logger.info(f"Data {self.model.__name__} success added.")
            await self._session.refresh(new_instance)
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error with add row to table: {e}")
            raise e
        return new_instance

    async def add_many(self, instances: List[BaseModel]) -> List[T]:
        # Save many values in the table
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        logger.info(f"Saving few rows {self.model.__name__}. Count: {len(values_list)}")
        new_instances = [self.model(**values) for values in values_list]
        self._session.add_all(new_instances)
        try:
            await self._session.commit()
            logger.info(f"Success saved {len(new_instances)} rows.")
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error in many saving: {e}")
            raise e
        return new_instances

    async def update(self, filters: BaseModel, values: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f"Updating columns {self.model.__name__} by filter: {filter_dict} with options: {values_dict}")
        query = (
            sqlalchemy_update(self.model)
            .where(*[getattr(self.model, k) == v for k, v in filter_dict.items()])
            .values(**values_dict)
            .execution_options(synchronize_session="fetch")
        )
        try:
            result = await self._session.execute(query)
            await self._session.commit()
            logger.info(f"Updated {result.rowcount} rows.")
            return result.rowcount
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Error in Update method: {e}")
            raise e

    async def delete(self, session: AsyncSession, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        logger.info(f"Delete method {self.model.__name__} by filter: {filter_dict}")
        if not filter_dict:
            logger.error("Required minimum one argument for delete")
            raise ValueError("Required minimum one argument for delete")

        query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
        try:
            result = await session.execute(query)
            await session.commit()
            logger.info(f"Deleted {result.rowcount}.")
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error when tried delete row: {e}")
            raise e
