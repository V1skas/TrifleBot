from bots.base import AbstractBot, menu_items, MenuPages, MenuItem, BotRequestData
from declarative_data.datasets import (UserActions, SessionStates, OrderData, ServiceData, BalanceData, TaskType,
                                       TaskData, TaskResultData, BotsData)
from database.module import DatabaseModule
from database.models import Session
from external.core_module import CoreModule
from external.core_module_lisener import CoreModuleLisener

from typing import List, Dict, Any
from datetime import date
import calendar

import logging
logger = logging.getLogger()


def calculate_payment(monthly_price, balance):
    if monthly_price is None or balance is None:
        return None

    monthly_price = float(monthly_price)
    balance = float(balance)

    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    day_of_month = today.day

    price_per_day = monthly_price / days_in_month

    if balance < 0:
        start_day = day_of_month
    else:
        start_day = day_of_month + 1

    remaining_days = max(0, days_in_month - start_day + 1)
    total_cost = price_per_day * remaining_days

    if balance > 0:
        total_cost -= balance

    return max(0, round(total_cost, 2))


class MsgFormatter:
    @classmethod
    def order_data(cls, data: Dict[str, Any]):
        return (f"Номер договору: {data.get(OrderData.number, 'None')}\n"
                f"Ідентифікатор о/р: {data.get(OrderData.id_ls, 'None')}\n"
                f"Оплата на місяць: {data.get(OrderData.tariff, 'None')} грн")

    @classmethod
    def service_data(cls, data: Dict[str, Any]):
        return (f"ІД сервісу: {data.get(ServiceData.id, 'None')}\n"
                f"IP сервісу: {data.get(ServiceData.ip, 'None')}")

    @classmethod
    def balance_data(cls, data: Dict[str, Any]):
        return (f"Номер договору: {data.get(BalanceData.number, 'None')}\n"
                f"Тариф: {data.get(BalanceData.tariff, 'None')}\n\n"
                f"Поточний баланс: {data.get(BalanceData.balance, 'None')}\n"
                f"Статус: {data.get(BalanceData.status, 'None')}\n"
                #f"Рекомендована сума поповнення: {calculate_payment(data.get(BalanceData.tariff, None), data.get(BalanceData.balance, None))}\n\n"
                f"---------------------------------------\n"
                f"Ідентифікатор о/р: {data.get(BalanceData.id_ls, 'None')}\n"
                f"Компанія виконавець: {data.get(BalanceData.company, 'None')}\n"
                f"Реквізити: {data.get(BalanceData.details, 'None')}")

    @classmethod
    def error(self):
        return "В ході виконання запиту сталася помилка, спробуйте ще раз."


class FatherBot(CoreModuleLisener):
    core: CoreModule
    dbm: DatabaseModule
    bots: Dict[int, AbstractBot]
    actions_handlers: Dict[int, Any] = {}
    task_result_handlers: Dict[str, Any] = {}
    sessions: Dict[str, Dict[int, Any]] = {}

    def __init__(self, core: CoreModule, dbm: DatabaseModule, bots: Dict[int, AbstractBot]):
        self.core = core
        self.dbm = dbm
        self.bots = bots

        self.actions_handlers[UserActions.auth] = self._auth_handler
        self.actions_handlers[UserActions.get_order_data] = self._get_order_handler
        self.actions_handlers[UserActions.get_service_data] = self._get_service_handler
        self.actions_handlers[UserActions.get_balance] = self._get_balance_handler
        self.actions_handlers[UserActions.exit] = self._exit_handler

        self.task_result_handlers[TaskType.auth] = self._auth_complete_handler
        self.task_result_handlers[TaskType.get_list_orders] = self._get_order_list_complete_handler
        self.task_result_handlers[TaskType.get_order_data] = self._get_order_data_complete_handler
        self.task_result_handlers[TaskType.get_list_services] = self._get_list_services_complete_handler
        self.task_result_handlers[TaskType.get_service_data] = self._get_service_data_complete_handler
        self.task_result_handlers[TaskType.get_balance] = self._get_balance_complete_handler

    async def load_sessions(self):
        self.sessions = (await self.dbm.get_sessions()).copy()

    async def exec_user_action(self, action: MenuItem, session_id: str, session_provider: int, data: Dict):
        logger.info(f"[INFO][FatherBot] Call exec_user_action for user: [{data.get(BotsData.phone_number)}]"
              f"[{session_id}][{session_provider}]")
        #if self.sessions.get(session_id) is None or self.sessions.get(session_id, SessionStates.free)[Session.Columns.CURRENT_STATE] == SessionStates.free:
        await self.actions_handlers[action.index](action, session_id, session_provider, data)
        #else:
        #    print(f"[Info] Action handler don`t find. session_id: {session_id}")

    async def task_complete(self, task: Dict[str, Any], result_task: Dict[str, Any]):
        await self.task_result_handlers[task[TaskData.type]](result_task, task[TaskData.id_session], task[TaskData.session_provider])
        #logger.info(f"[INFO][FatherBot] Call task_complete for user: [{self.sessions[task[TaskData.id_session]][Session.Columns.PHONE_NUMBER]}]"
        #      f"[{task[TaskData.id_session]}][{task[TaskData.session_provider]}]")

    async def send_mes(self, phone_number: str, message: str):
        logger.info(f"[INFO][FatherBot] Call send for user: {phone_number}")
        for _, value in self.sessions.items():
            if value[Session.Columns.PHONE_NUMBER] is phone_number:
                await self.bots[value[Session.Columns.SESSION_PROVIDER]].send(value[Session.Columns.ID_SESSION],
                                                                              message, menu_items[MenuPages.empty])

    async def send_many(self, phone_numbers: List[str], message: str):
        logger.info(f"[INFO][FatherBot] Call send_many")
        for _, value in self.sessions.items():
            if value[Session.Columns.PHONE_NUMBER] in phone_numbers:
                await self.bots[value[Session.Columns.SESSION_PROVIDER]].send(value[Session.Columns.ID_SESSION],
                                                                              message, menu_items[MenuPages.empty])

    async def send_all(self, message: str):
        logger.info(f"[INFO][FatherBot] Call send for all")
        for _, value in self.sessions.items():
            await self.bots[value[Session.Columns.SESSION_PROVIDER]].send(value[Session.Columns.ID_SESSION],
                                                                          message, menu_items[MenuPages.empty])

    async def send_balance(self, phone_number: str, data: Dict[str, Any]):
        logger.info(f"[INFO][FatherBot] Call send_balance")
        for _, value in self.sessions.items():
            if value[Session.Columns.PHONE_NUMBER] is phone_number:
                await self.bots[value[Session.Columns.SESSION_PROVIDER]].send(value[Session.Columns.ID_SESSION],
                                                                              MsgFormatter.balance_data(data),
                                                                              menu_items[MenuPages.empty])

    async def send_err(self, session_id: str):
        logger.info(f"[INFO][FatherBot] Call send_err for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{self.sessions[session_id][Session.Columns.SESSION_PROVIDER]}]")
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
        self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.complete
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.free
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
        await self.bots[self.sessions[session_id][Session.Columns.SESSION_PROVIDER]].send(session_id,
                                                                                          MsgFormatter.error(),
                                                                                          [])

    async def _auth_handler(self, action: MenuItem, session_id: str, session_provider: int, data: Any):
        self.sessions[session_id] = {Session.Columns.ID_SESSION: session_id,
                                     Session.Columns.CURRENT_ACTION: UserActions.auth,
                                     Session.Columns.CURRENT_STATE: SessionStates.waiting_process_query,
                                     Session.Columns.SESSION_PROVIDER: session_provider,
                                     Session.Columns.PHONE_NUMBER: str(data.get(BotsData.phone_number)),
                                     Session.Columns.CURRENT_MENU: MenuPages.empty }
        await self.dbm.add_session(self.sessions[session_id])
        logger.info(
            f"[INFO][FatherBot] Call _auth_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
            f"[{session_id}][{session_provider}]")
        await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.id_session: session_id,
                                                              TaskData.session_provider: session_provider,
                                                              TaskData.type: TaskType.auth, TaskData.data: data})

    async def _get_order_handler(self, action: MenuItem, session_id: str, session_provider: int, data: Dict):
        logger.info(f"[INFO][FatherBot] Call _get_order_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        if self.sessions[session_id][Session.Columns.CURRENT_ACTION] != UserActions.get_order_data:
            self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.get_order_data
            self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.type: TaskType.get_list_orders,
                                                                  TaskData.id_session: session_id,
                                                                  TaskData.session_provider: session_provider,
                                                                  TaskData.data: self.sessions[session_id][Session.Columns.PHONE_NUMBER]})

        elif self.sessions[session_id][Session.Columns.CURRENT_MENU] == MenuPages.orders:
            self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.get_order_data
            self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.id_session: session_id,
                                                                      TaskData.session_provider: session_provider,
                                                                      TaskData.type: TaskType.get_order_data,
                                                                      TaskData.data: action.name})
        else:
            logger.warning(f"[ERROR][FatherBot] Uncorrect scenario for request _get_order_handler\n"
                  f"User data: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}][{session_id}][{session_provider}]")

    async def _get_service_handler(self, action: MenuItem, session_id: str, session_provider: int, data: Dict):
        logger.info(f"[INFO][FatherBot] Call _get_service_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        if self.sessions[session_id][Session.Columns.CURRENT_ACTION] != UserActions.get_service_data:
            self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.get_service_data
            self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.type: TaskType.get_list_orders,
                                                                  TaskData.id_session: session_id,
                                                                  TaskData.session_provider: session_provider,
                                                                  TaskData.data: self.sessions[session_id][Session.Columns.PHONE_NUMBER]})

        elif self.sessions[session_id][Session.Columns.CURRENT_MENU] == MenuPages.orders:
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.id_session: session_id,
                                                                  TaskData.session_provider: session_provider,
                                                                  TaskData.type: TaskType.get_list_services,
                                                                  TaskData.data: action.name})

        elif self.sessions[session_id][Session.Columns.CURRENT_MENU] == MenuPages.services:
            self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.get_service_data
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.id_session: session_id,
                                                                  TaskData.session_provider: session_provider,
                                                                  TaskData.type: TaskType.get_service_data,
                                                                  TaskData.data: action.name})

        else:
            logger.warning(f"[ERROR][FatherBot] Uncorrect scenario for request _get_service_handler.\n"
                  f"User data: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}][{session_id}][{session_provider}]")

    async def _get_balance_handler(self, action: MenuItem, session_id: str, session_provider: int, data: Dict):
        logger.info(f"[INFO][FatherBot] Call _get_balance_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        if self.sessions[session_id][Session.Columns.CURRENT_ACTION] != UserActions.get_balance:
            self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.get_balance
            self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.orders
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.type: TaskType.get_list_orders,
                                                                  TaskData.id_session: session_id,
                                                                  TaskData.session_provider: session_provider,
                                                                  TaskData.data: {"phone_number": self.sessions[session_id][
                                                                                      Session.Columns.PHONE_NUMBER]}})

        elif self.sessions[session_id][Session.Columns.CURRENT_MENU] == MenuPages.orders:
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.type: TaskType.get_balance,
                                                                  TaskData.id_session: session_id,
                                                                  TaskData.session_provider: session_provider,
                                                                  TaskData.data: {"order_number": action.name,
                                                                                  "phone_number": self.sessions[session_id][Session.Columns.PHONE_NUMBER]}})

        else:
            logger.warning(f"[ERROR][FatherBot] Uncorrect scenario for request _get_balance_handler.\n"
                  f"User data: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}][{session_id}][{session_provider}]")

    async def _exit_handler(self, action: MenuItem, session_id: str, session_provider: int, data: Dict):
        logger.info(f"[INFO][FatherBot] Call _exit_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.free
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
        self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.complete
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
        await self.bots[session_provider].send(session_id, "Головне меню", menu_items[MenuPages.main])

    async def _auth_complete_handler(self, data: Dict[str, Any], session_id: str, session_provider: int):
        if data.get("auth") is None or data.get("auth") is False:
            self.sessions.pop(session_id)
            await self.bots[session_provider].send(session_id, "Клієнта з таким номером телефону не знайдено.\n\n"
                                                                    "Перевірте дані у власному кабінеті, або оновіть їх "
                                                                    "зв'язавшись з відділом договорів:\n"
                                                                    "Телефон: (056)-731-99-11,\n"
                                                                    "         (067)-731-99-11,\n"
                                                                    "         (050)-731-99-11\n"
                                                                    "Пошта: accounts@trifle.net\n\n"
                                                                    "Для повторної авторизації надішліть /auth.",
                                                   menu_items[MenuPages.empty])
            return

        self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.complete
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.free
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
        await self.bots[session_provider].send(session_id, "Верифіковано!\n\n"
                                                           "Усі доступні функції бота можна викликати у меню знизу.",
                                               menu_items[MenuPages.main])
        logger.info(f"[INFO][FatherBot] Call _auth_complete_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")

    async def _get_order_list_complete_handler(self, data: Dict[str, Any], session_id: str, session_provider: int):
        logger.info(f"[INFO][FatherBot] Call _get_order_list_complete_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        if data.get("orders_numbers", None) is None:
            self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.complete
            self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.free
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.bots[session_provider].send(session_id, "Доступних договорів не знайдено.\n"
                                                         "Перевірте налаштування у власному кабінеті.",
                                             menu_items[MenuPages.main])
            return

        orders_menu: List[MenuItem] = menu_items[MenuPages.orders].copy()
        for number in data["orders_numbers"]:
            orders_menu.insert(0, MenuItem(number, self.sessions[session_id][Session.Columns.CURRENT_ACTION]))
        await self.bots[session_provider].send(session_id, "Оберіть номер договору у меню", orders_menu)
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.orders
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_user_input
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))

    async def _get_order_data_complete_handler(self, data: Dict[str, Any], session_id: str, session_provider: int):
        logger.info(f"[INFO][FatherBot] Call _get_order_data_complete_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.complete
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.free
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
        await self.bots[session_provider].send(session_id, MsgFormatter.order_data(data), menu_items[MenuPages.main])

    async def _get_list_services_complete_handler(self, data: Dict[str, Any], session_id: str, session_provider: int):
        logger.info(f"[INFO][FatherBot] Call _get_list_services_complete_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        if data.get("services_id", None) is None:
            self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.complete
            self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
            self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.free
            await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
            await self.bots[session_provider].send(session_id, "Доступних сервісів/пакетів не знайдено.\n",
                                                   menu_items[MenuPages.main])
            return

        orders_menu: List[MenuItem] = menu_items[MenuPages.services].copy()
        for number in data["services_id"]:
            orders_menu.insert(0, MenuItem(number, self.sessions[session_id][Session.Columns.CURRENT_ACTION]))
        await self.bots[session_provider].send(session_id, "Оберіть id сервісу/пакету у меню", orders_menu)
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.services
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_user_input
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))

    async def _get_service_data_complete_handler(self, data: Dict[str, Any], session_id: str, session_provider: int):
        logger.info(f"[INFO][FatherBot] Call _get_service_data_complete_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.complete
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.main
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.free
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
        await self.bots[session_provider].send(session_id, MsgFormatter.service_data(data), menu_items[MenuPages.main])

    async def _get_balance_complete_handler(self, data: Dict[str, Any], session_id: str, session_provider: int):
        logger.info(f"[INFO][FatherBot] Call _get_balance_complete_handler for user: [{self.sessions[session_id][Session.Columns.PHONE_NUMBER]}]"
              f"[{session_id}][{session_provider}]")
        self.sessions[session_id][Session.Columns.CURRENT_ACTION] = UserActions.get_balance
        self.sessions[session_id][Session.Columns.CURRENT_MENU] = MenuPages.orders
        self.sessions[session_id][Session.Columns.CURRENT_STATE] = SessionStates.waiting_process_query
        await self.dbm.update_session(Session.obj_from_dict(self.sessions[session_id]))
        await self.bots[session_provider].send(session_id, MsgFormatter.balance_data(data), menu_items[MenuPages.orders])
        await self.core.add_task(CoreModule.Recipients.BOSS, {TaskData.type: TaskType.get_list_orders,
                                                                  TaskData.id_session: session_id,
                                                                  TaskData.session_provider: session_provider,
                                                                  TaskData.data: {"phone_number": self.sessions[session_id][
                                                                                      Session.Columns.PHONE_NUMBER]}})

    async def check_work(self):
        print("Father bot work!")
        await self.dbm.check_work()