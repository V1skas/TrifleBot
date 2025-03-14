from asyncio import run

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from database.base import DATABASE_URL
from database.models import Session, Task
from database.dao.dao import SessionDAO, TaskDAO

from typing import Any, List, Dict


class DatabaseModule:
    engine: AsyncEngine
    asyncSession: async_sessionmaker[AsyncSession]

    @staticmethod
    def connection(commit: bool = False):
        def decorator(method):
            async def wrapper(self, *args, **kwargs):
                async with self.asyncSession() as session:
                    try:
                        result = await method(self, *args, session=session, **kwargs)
                        if commit:
                            await session.commit()
                            print("Commited!")
                        return result
                    except Exception as e:
                        await session.rollback()
                        raise e
                    finally:
                        await session.close()

            return wrapper

        return decorator

    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(url=DATABASE_URL)
        self.asyncSession = async_sessionmaker(self.engine, expire_on_commit=False)

    @connection(commit=True)
    async def add_session(self, instance: Any, session: AsyncSession):
        await SessionDAO.add(session, instance)

    @connection(commit=True)
    async def update_session(self, instance: Session, session: AsyncSession):
        await SessionDAO.update_one(session, instance)

    @connection()
    async def get_sessions(self, session: AsyncSession):
        list_session_models: List[Session] = await SessionDAO.get_all(session)
        result: Dict[str, Dict[str, Any]] = {}

        for model in list_session_models:
            tmp = model.dict()
            print(tmp)
            result[str(tmp[Session.Columns.ID_SESSION])] = tmp

        return result
    
    @connection(commit=True)
    async def add_task(self, instance: Task, session: AsyncSession):
        await TaskDAO.add(session, instance)

    @connection(commit=True)
    async def remove_task(self, id: str, session: AsyncSession):
        pass

    @connection()
    async def get_users_keys_map(self, session: AsyncSession):
        await SessionDAO.get_user_keys_map(session)

    @connection(commit=True)
    async def update_user_keys_map(self, id: str, keys_map: dict, session: AsyncSession):
        await SessionDAO.add_or_update_keys_map_by_id(session, id, keys_map)


    async def check_work(self):
        print("Database module work!")