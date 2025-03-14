from typing import Any, TypeVar, Generic, List, Dict
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import Base


T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model = type[T]

    @classmethod
    async def add(cls, session: AsyncSession, data: Dict[int, Any]) -> Any:
        obj = cls.model.obj_from_dict(data)
        await session.merge(obj)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return obj

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: list[type[T]]) -> list[T]:
        session.add_all(instances)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return instances

    @classmethod
    async def update_one(cls, session: AsyncSession, new_instance: type[T]):
        instance = await session.get(cls.model, new_instance.primary_key_value())
        instance.from_obj(new_instance)
        await session.flush(instance)
        return instance

    @classmethod
    async def update_many(cls, session: AsyncSession, new_instances: List[type[T]]):
        list_instances: List[type[T]]
        for new_instance in new_instances:
            instance: type[T]= await session.get(cls.model, new_instance.primary_key_value())
            instance.from_obj
            list_instances.append()


    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, data_id: Any):
        query = select(cls.model).filter_by(id=data_id)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        return record

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        records = result.scalars().all()
        print(records)
        return records