import abc
from typing import List, Dict, Any
from declarative_data.datasets import MenuPages, UserActions
from enum import IntEnum, auto


class BotRequestData(IntEnum):
    phone_number = auto()
    order_number = auto()


class MenuItem:
    name: str
    index: int

    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index


menu_items: Dict[int, List[MenuItem]] = {MenuPages.empty: [],
                                         MenuPages.main: [#MenuItem("Договори", UserActions.get_order_data),
                                                          #MenuItem("Сервіси/Пакети", UserActions.get_service_data),
                                                          MenuItem("Баланси", UserActions.get_balance)],
                                         MenuPages.orders: [MenuItem("<- Повернутись", UserActions.exit)],
                                         MenuPages.services: [MenuItem("<- Повернутись", UserActions.exit)],
                                         MenuPages.clear: None}


class AbstractBot(abc.ABC):
    session_provider: int
    async def send(self, session_id: str, msg: str, menu: List[MenuItem]):
        pass