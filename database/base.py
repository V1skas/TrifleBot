from sqlalchemy.orm import DeclarativeBase
from config import settings
import abc
from typing import Dict

DATABASE_URL = settings.get_db_url()


class Base(DeclarativeBase):

    @classmethod
    @abc.abstractmethod
    async def obj_from_dict(cls, data: Dict):
        pass

    @abc.abstractmethod
    async def from_dict(self, data: Dict):
        pass

    @abc.abstractmethod
    async def from_obj(self, obj: 'Base'):
        pass

    def primary_key_value(self):
        return getattr(self, self.__mapper__.primary_key[0].name)
