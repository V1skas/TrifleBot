from asyncio import sleep
from time import time

from aiohttp import web
from enum import StrEnum, Enum
from typing import Any, Dict, List

from config import settings
from declarative_data.datasets import CoreModuleResponseData, ListErrors, RequestArgsNames, TaskResultData, TaskData, \
    MessageData, MessageType

from external.core_module_lisener import CoreModuleLisener

import logging
from logging import warn, info, error
logger = logging.getLogger()


def generate_id():
    return str(int(time() * 1000))


class CoreModule:
    class Recipients(Enum):
        BOSS = settings.BOSS_IP

    host: str
    port: int
    app: Any
    bot = CoreModuleLisener

    tasks_list: Dict[str, List[Dict[str, Any]]] = {}

    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self._setup_routes()

    def get_task_by_id(self, id: str, recipient: str):
        for i in range(len(self.tasks_list[recipient])):
            if self.tasks_list[recipient][i][TaskData.id] == id:
                return self.tasks_list[recipient].pop(i)
        return None

    async def handle_get_tasks(self, request):
        logger.info("[INFO][CoreModule] Call handle_get_tasks")
        client_ip: str = str(request.remote)

        for item in self.Recipients:
            if client_ip not in item.value:
                logger.info(f"[INFO][CoreModule] get_tasks operation denied for: {client_ip}")
                return web.json_response({CoreModuleResponseData.success: False,
                                          CoreModuleResponseData.err_code: ListErrors.operation_denied,
                                          CoreModuleResponseData.message: "Operation denied!"})
            else:
                client_ip = item.name


        count = request.query.get(str(RequestArgsNames.count_task), None)

        if not count or not count.isdigit():
            logger.warning("Invalid or missing 'count' parameter!")
            return web.json_response({CoreModuleResponseData.success: False,
                                      CoreModuleResponseData.err_code: ListErrors.uncorrected_request,
                                      CoreModuleResponseData.message: "Invalid or missing 'count' parameter!",
                                      CoreModuleResponseData.task_in_queue: len(self.tasks_list.get[client_ip])})

        count = int(count)

        tasks = []
        list_t = self.tasks_list.get(client_ip, None)

        if list_t is None:
            logger.info("Queue tasks empty.")
            return web.json_response({CoreModuleResponseData.success: False,
                                      CoreModuleResponseData.err_code: ListErrors.task_queue_empty,
                                      CoreModuleResponseData.message: "Queue tasks empty.",
                                      CoreModuleResponseData.task_in_queue: 0})

        if count > len(list_t):
            tasks = list_t
        else:
            for i in range(count):
                tasks.append(list_t[i])

        return web.json_response({CoreModuleResponseData.success: True,
                                  CoreModuleResponseData.data: tasks,
                                  CoreModuleResponseData.task_in_queue: len(self.tasks_list[client_ip])})

    async def handle_task_complete(self, request):
        logger.info("[INFO][CoreModule] Call handle_task_complete")
        task_result = await request.json()
        print(task_result)
        client_ip: str = str(request.remote)

        for item in self.Recipients:
            if client_ip not in item.value:
                logger.info(f"[INFO][CoreModule] get_tasks operation denied for: {client_ip}")
                return web.json_response({CoreModuleResponseData.success: False,
                                          CoreModuleResponseData.err_code: ListErrors.operation_denied,
                                          CoreModuleResponseData.message: "Operation denied!"})
            else:
                client_ip = item.name

        if not isinstance(task_result, dict):
            logger.warning("Invalid request format!")
            return web.json_response({CoreModuleResponseData.success: False,
                                      CoreModuleResponseData.data: task_result,
                                      CoreModuleResponseData.err_code: ListErrors.uncorrected_request,
                                      CoreModuleResponseData.message: "Invalid request format!",
                                      CoreModuleResponseData.task_in_queue: len(self.tasks_list[client_ip])})

        task: Dict[str, Any] = {}

#        try:
        task = self.get_task_by_id(task_result[TaskResultData.id], client_ip)

        if task is None:
            logger.warning("Invalid id task.")
            return web.json_response({CoreModuleResponseData.success: False,
                                      CoreModuleResponseData.data: task_result,
                                      CoreModuleResponseData.err_code: ListErrors.uncorrected_request,
                                      CoreModuleResponseData.message: "Invalid id task.",
                                      CoreModuleResponseData.task_in_queue: len(self.tasks_list[client_ip])})

        if not task_result[TaskResultData.success]:
            logger.warning(
                f"[ERROR][CoreModule] Server can`t process task:\n#{task_result[TaskResultData.err_core]} {task_result[TaskResultData.message]}")
            await self.bot.send_err(task[TaskData.id_session])
            return web.json_response({CoreModuleResponseData.success: True})

        await self.bot.task_complete(task, task_result[TaskResultData.data])
        return web.json_response({CoreModuleResponseData.success: True})

#        except KeyError as e:
#            logger.warning(f"[ERROR][CoreModule] Invalid request format! Missed key.\nDetail task result: {task_result}\n"
#                  f"Detail task: {task}")
#            await self.bot.send_err(task[TaskData.id_session])
#            return web.json_response({CoreModuleResponseData.success: False,
#                                      CoreModuleResponseData.data: task_result,
#                                      CoreModuleResponseData.err_code: ListErrors.uncorrected_request,
#                                      CoreModuleResponseData.message: "Invalid request format. "
#                                                                      "Missed key.",
#                                      CoreModuleResponseData.task_in_queue: len(self.tasks_list[client_ip])})

#        except Exception as e:
#            logger.warning(f"[ERROR][CoreModule] Undefined error.\n"
#                  f"{e}")
#            await self.bot.send_err(task[TaskData.id_session])
#            return web.json_response({CoreModuleResponseData.success: False,
#                                      CoreModuleResponseData.data: task_result,
#                                      CoreModuleResponseData.err_code: ListErrors.undedined_err,
#                                      CoreModuleResponseData.message: "Undefined error.",
#                                      CoreModuleResponseData.task_in_queue: len(self.tasks_list[client_ip])})

    async def handle_send(self, request):
        logger.info("[INFO][CoreModule] Call handle_send")
        client_ip: str = str(request.remote)

        for item in self.Recipients:
            if client_ip not in item.value:
                logger.info(f"[INFO][CoreModule] get_tasks operation denied for: {client_ip}")
                return web.json_response({CoreModuleResponseData.success: False,
                                          CoreModuleResponseData.err_code: ListErrors.operation_denied,
                                          CoreModuleResponseData.message: "Operation denied!"})
            else:
                client_ip = item.name

        data = await request.json()

        if not isinstance(data, dict):
            return web.json_response({CoreModuleResponseData.success: False,
                                      CoreModuleResponseData.data: data,
                                      CoreModuleResponseData.err_code: ListErrors.uncorrected_request,
                                      CoreModuleResponseData.message: "Invalid request format!"})

        try:
            if data[MessageData.type] == MessageType.send_one:
                await self.bot.send_mes(data[MessageData.phone_number], data[MessageData.message])
            elif data[MessageData.type] == MessageType.send_many:
                await self.bot.send_many(data[MessageData.phone_number], data[MessageData.message])
            elif data[MessageData.type] == MessageType.send_balance:
                await self.bot.send_balance(data[MessageData.phone_number], data[MessageData.data])

        except KeyError as e:
            logger.warning(f"[ERROR][CoreModule] Invalid request format! Missed key.\nDetail:{data}")
            return web.json_response({CoreModuleResponseData.success: False,
                                      CoreModuleResponseData.data: data,
                                      CoreModuleResponseData.err_code: ListErrors.uncorrected_request,
                                      CoreModuleResponseData.message: "Invalid request format. "
                                                                      "Missed key."})

        except Exception as e:
            logger.warning(f"[ERROR] Undefined error.\n"
                  f"{e}")
            return web.json_response({CoreModuleResponseData.success: False,
                                      CoreModuleResponseData.data: data,
                                      CoreModuleResponseData.err_code: ListErrors.undedined_err,
                                      CoreModuleResponseData.message: "Undefined error."})

    async def add_task(self, recipient: Recipients, task: Dict[str, Any]):
        logger.info("[INFO][CoreModule] Call add_task")
        task[TaskData.id] = generate_id()
        if recipient in self.tasks_list:
            self.tasks_list[recipient.name].append(task)
        else:
            self.tasks_list[recipient.name] = [task]
        logger.info(f"[INFO][CoreModule] New task:\n{task}")

    async def handle_check_work(self, request):
        logger.info("Core module work!")
        await self.bot.check_work()
        return web.json_response({CoreModuleResponseData.success: True,
                                  CoreModuleResponseData.task_in_queue: len(self.tasks_list.get(str(request.remote), []))})

    def _setup_routes(self):
        self.app.router.add_get('/core/tasks', self.handle_get_tasks)
        self.app.router.add_post('/core/tasks', self.handle_task_complete)
        self.app.router.add_post('/core/send', self.handle_send)
        self.app.router.add_get('/core/check_work', self.handle_check_work)

    async def run(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"HTTP сервер запущен на http://{self.host}:{self.port}")

