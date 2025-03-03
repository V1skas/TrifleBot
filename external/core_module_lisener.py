import abc
from typing import List, Dict, Any


class CoreModuleLisener(abc.ABC):
    @abc.abstractmethod
    async def send_mes(self, phone_number: str, message: str):
        pass

    @abc.abstractmethod
    async def send_many(self, phone_numbers: List[str], message: str):
        pass

    @abc.abstractmethod
    async def send_balance(self, phone_number: str, data: Dict[str, Any]):
        pass

    @abc.abstractmethod
    async def send_all(self, message: str):
        pass

    @abc.abstractmethod
    async def send_err(self, session_id: str):
        pass

    @abc.abstractmethod
    async def task_complete(self, task: Dict[str, Any], result_task: Dict[str, Any]):
        pass

    @abc.abstractmethod
    async def check_work(self):
        pass