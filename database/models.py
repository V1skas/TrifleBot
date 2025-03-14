from enum import IntEnum, auto
from typing import Dict

from sqlalchemy import String
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base
from declarative_data.datasets import MenuPages, SessionStates, UserActions


class Session(Base):
    __tablename__ = 'sessions'

    class Columns:
        ID_SESSION = 0
        CURRENT_MENU = 1
        SESSION_PROVIDER = 2
        CURRENT_STATE = 3
        CURRENT_ACTION = 4
        PHONE_NUMBER = 5
        USER_KEYS_MAP = 6

    id_session: Mapped[str] = mapped_column(String(20), primary_key=True)
    current_menu: Mapped[int] = mapped_column(default=MenuPages.empty, server_default=str(MenuPages.empty))
    session_provider: Mapped[int]
    current_state: Mapped[int] = mapped_column(default=SessionStates.free, server_default=str(SessionStates.free))
    current_action: Mapped[int] = mapped_column(default=UserActions.complete, server_default=str(UserActions.complete))
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    user_keys_map: Mapped[dict] = mapped_column(JSON, nullable=True)


    @classmethod
    def obj_from_dict(cls, data: dict):
        return Session(id_session=data.get(cls.Columns.ID_SESSION),
                       current_menu=data.get(cls.Columns.CURRENT_MENU),
                       session_provider=data.get(cls.Columns.SESSION_PROVIDER),
                       current_state=data.get(cls.Columns.CURRENT_STATE),
                       current_action=data.get(cls.Columns.CURRENT_ACTION),
                       phone_number=data.get(cls.Columns.PHONE_NUMBER),
                       user_keys_map=data.get(cls.Columns.USER_KEYS_MAP)
                       )

    def from_dict(self, data: Dict):
        self.id_session = data.get(self.Columns.ID_SESSION)
        self.current_menu = data.get(self.Columns.CURRENT_MENU)
        self.session_provider = data.get(self.Columns.SESSION_PROVIDER)
        self.current_state = data.get(self.Columns.CURRENT_STATE)
        self.current_action = data.get(self.Columns.CURRENT_ACTION)
        self.phone_number = data.get(self.Columns.PHONE_NUMBER)
        self.user_keys_map = data.get(self.Columns.USER_KEYS_MAP)

    def from_obj(self, obj: 'Session'):
        self.id_session = obj.id_session if obj.id_session is not None else self.id_session
        self.current_menu = obj.current_menu if obj.current_menu is not None else self.current_menu
        self.session_provider = obj.session_provider if obj.session_provider is not None else self.session_provider
        self.current_state = obj.current_state if obj.current_state is not None else self.current_state
        self.current_action = obj.current_action if obj.current_action is not None else self.current_action
        self.phone_number = obj.phone_number if obj.phone_number is not None else self.phone_number
        self.user_keys_map = obj.user_keys_map if obj.user_keys_map is not None else self.user_keys_map

    def dict(self):
        return {self.Columns.ID_SESSION: self.id_session,
                self.Columns.CURRENT_MENU: self.current_menu,
                self.Columns.CURRENT_STATE: self.current_state,
                self.Columns.CURRENT_ACTION: self.current_action,
                self.Columns.SESSION_PROVIDER: self.session_provider,
                self.Columns.PHONE_NUMBER: self.phone_number,
                self.Columns.USER_KEYS_MAP: self.user_keys_map}

class Task(Base):
    __tablename__ = "tasks"

    class Columns:
        ID = "id"
        TYPE = "type"
        ID_SESSION = "id_session"
        SESSION_PROVIDER = "session_provider"
        DATA = "data"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[int]
    id_session: Mapped[str] = mapped_column(String(36))
    session_provider: Mapped[int]
    data: Mapped[dict] = mapped_column(JSON)

    @classmethod
    def obj_from_dict(cls, data: dict):
        return Task(id=data.get(cls.Columns.ID),
                       type=data.get(cls.Columns.TYPE),
                       id_session=data.get(cls.Columns.ID_SESSION),
                       session_provider=data.get(cls.Columns.SESSION_PROVIDER),
                       data=data.get(cls.Columns.DATA)
                       )

    def from_dict(self, data: Dict):
        self.id = data.get(self.Columns.ID)
        self.type = data.get(self.Columns.TYPE)
        self.id_session = data.get(self.Columns.ID_SESSION)
        self.session_provider = data.get(self.Columns.SESSION_PROVIDER)
        self.data = data.get(self.Columns.DATA)

    def from_obj(self, obj: 'Task'):
        self.id = obj.id if obj.id is not None else self.id
        self.type = obj.type if obj.type is not None else self.type
        self.id_session = obj.id_session if obj.id_session is not None else self.id_session
        self.session_provider = obj.session_provider if obj.session_provider is not None else self.session_provider
        self.data = obj.data if obj.data is not None else self.data

    def dict(self):
        return {self.Columns.ID: self.id,
                self.Columns.TYPE: self.type,
                self.Columns.ID_SESSION: self.id_session,
                self.Columns.SESSION_PROVIDER: self.session_provider,
                self.Columns.DATA: self.data}
