from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy import select

from database.dao.base import BaseDAO
from database.models import Session, Task


class SessionDAO(BaseDAO[Session]):
    model = Session
    @classmethod
    async def update_one(cls, session: AsyncSession, new_instance):
        if not isinstance(cls.model, type) or not issubclass(cls.model, DeclarativeBase):
            raise ValueError(f"cls.model должен быть SQLAlchemy-моделью, а не {type(cls.model)}")

        pk_value = new_instance.primary_key_value()
        if pk_value is None:
            raise ValueError("primary_key_value() вернул None! Убедитесь, что ID указан.")

        try:
            instance = await session.get(cls.model, pk_value)
            if instance:
                for key, value in vars(new_instance).items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
            else:
                raise ValueError(f"Объект {cls.model.__name__} с ID {pk_value} не найден!")
        except NoInspectionAvailable:
            raise ValueError(f"Невозможно проинспектировать {cls.model}. Проверьте, передаётся ли модель SQLAlchemy.")
        
    @classmethod
    async def get_user_keys_map(cls, session: AsyncSession):
        query = select(cls.model.id_session, cls.model.user_keys_map)
        print(query)
        results = await session.execute(query)
        print(results)
        records = results.scalars().all()
        print(records)

    @classmethod
    async def add_or_update_keys_map_by_id(cls, session: AsyncSession, id: str, keys_map: dict):
        ses_obj: Session = await session.get(cls.model, id)
        ses_obj.user_keys_map = keys_map


class TaskDAO(BaseDAO[Task]):
    model = Task
    ...