from enum import IntEnum, StrEnum, Enum
from typing import NamedTuple


class MenuPages:
    empty = 0
    main = 1
    orders = 2
    services = 3,
    notification_settings = 4


class UserActions:
    complete = 0
    auth = 1
    get_order_data = 2
    get_service_data = 3
    get_balance = 4
    set_notification = 5
    exit = 6


class BotsData:
    phone_number = "phone_number"


class TaskData:
    id = "id"
    type = "type"
    id_session = "id_session"
    session_provider = "session_provider"
    data = "data"


class MessageData:
    type = "type"
    phone_number = "phone_number"
    message = "message"
    data = "data"


class MessageType:
    send_one = "send_one"
    send_many = "send_many"
    send_all = "send_all"
    send_balance = "send_balance"


class TaskResultData:
    id = "id"
    success = "success"
    data = "data"
    err_core = "err_code"
    message = "message"


class CoreModuleResponseData:
    success = "success"
    data = "data"
    err_code = "err_code"
    message = "message"
    task_in_queue = "task_in_queue"


class ListErrors:
    no_auth = 0
    no_available_orders = 1
    no_available_services = 2
    uncorrected_request = 3
    operation_denied = 4
    task_queue_empty = 5
    undedined_err = 6


class TaskType:
    auth = "auth"
    get_order_data = "get_order_data"
    get_service_data = "get_service_data"
    get_balance = "get_balance"
    set_notification = "set_notification"
    get_list_orders = "get_list_orders"
    get_list_services = "get_list_services"


class RequestArgsNames:
    count_task = "count"


class SessionProviders:
    telegram = 0
    viber = 1


class SessionStates:
    free = 0
    waiting_user_input = 1
    waiting_process_query = 2


class OrderData:
    number = "number"
    id_ls = "id_ls"
    tariff = "tariff"


class ServiceData:
    id = "id"
    ip = "ip"


class BalanceData:
    number = "number"
    tariff = "tariff"
    balance = "balance"
    to_pay = "to_pay"
    id_ls = "id_ls"
    company = "company"
    details = "details"
