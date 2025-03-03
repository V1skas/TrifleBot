from functools import wraps

from bots.base import AbstractBot, MenuItem
from bots.father_bot import FatherBot
from declarative_data.datasets import SessionProviders, UserActions, BotsData

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from typing import List, Dict

import asyncio
from config import settings

import logging
logger = logging.getLogger()

dp: Dispatcher = Dispatcher()
bot: Bot
father: FatherBot

user_keys_map: Dict[str, Dict[str, int]] = {}


class TelegramBot(AbstractBot):
    session_provider = int(SessionProviders.telegram)

    def __init__(self, token: str, fa: FatherBot):
        global dp
        global bot
        global father
        bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        father = fa

    async def run(self):
        global dp
        global bot
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    async def send(self, session_id: str, msg: str, menu: List[MenuItem]):
        global bot
        global user_keys_map
        if len(menu) > 0:
            builder = ReplyKeyboardBuilder()
            if user_keys_map.get(session_id, None) is not None:
                user_keys_map[session_id].clear()
            else:
                user_keys_map[session_id] = {}
            for item in menu:
                builder.add(types.KeyboardButton(text=item.name))
                user_keys_map[session_id][item.name] = item.index
            builder.adjust(2)
            global bot
            await bot.send_message(session_id, msg, reply_markup=builder.as_markup(resize_keyboard=True))
        else:
            await bot.send_message(session_id, msg)


@dp.message(Command("start"))
async def com_start(message: Message):
    global user_keys_map
    user_keys_map[str(message.from_user.id)] = {}
    keyboard = ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Далі",
                                                                   request_contact=True)]], resize_keyboard=True)
    await message.answer("Для роботи з ботом підтримки Трайфл, необхідно підтвердити Ваші контактні дані "
                         "(Номер телефону).\n\n"
                         "Для цього натисніть на кнопку \"Далі\".",
                         reply_markup=keyboard)


@dp.message(F.contact)
async def com_phn_send(message: Message):
    global father
    try:
        if message.from_user.id != message.contact.user_id:
            await message.answer(f"Контакт не відповідає відправнику!")
            return

        phone_number = message.contact.phone_number
        if phone_number[0] != '+':
            phone_number = '+'+phone_number
        await message.answer(f"Очікуйте підтвердження..")
        await father.exec_user_action(MenuItem("", UserActions.auth), str(message.from_user.id),
                                      SessionProviders.telegram,
                                      {BotsData.phone_number: phone_number})

    except AttributeError as e:
        await message.answer(f"Контактні дані не надано.")
        logger.warning(f"AttributeError: {e}")

    #except Exception as e:
    #    print(f"[ERROR][TelegramBot] Unable exception in 'com_phn_send'.\n"
    #          f"Client info: {message.from_user}\n"
    #          f"Exception: {e}")

#@dp.message(F.text == "Договори")
#async def com_orders_list(message: Message):
#    await father.exec_user_action(MenuItem("Договори", UserActions.get_order_data), str(message.from_user.id),
#                                  SessionProviders.telegram, {})

#@dp.message(F.text == "Сервіси/Пакети")
#async def com_services_list(message: Message):
#    await father.exec_user_action(MenuItem("Сервіси/Пакети", UserActions.get_service_data), str(message.from_user.id),
#                                  SessionProviders.telegram, {})

@dp.message(F.text == "Баланси")
async def com_balances(message: Message):
    await father.exec_user_action(MenuItem("Баланси", UserActions.get_balance), str(message.from_user.id),
                                  SessionProviders.telegram, {})

@dp.message(F.text)
async def com_some_text(message: Message):
    global user_keys_map
    if user_keys_map[str(message.from_user.id)].get(message.text, None) is None:
        await message.answer("Невідома команда.")
        return

    global father
    await father.exec_user_action(MenuItem(str(message.text), user_keys_map[str(message.from_user.id)][message.text]),
                                  str(message.from_user.id),
                                  SessionProviders.telegram,
                                  {})


#async def main():
#    bt = TelegramBot(settings.TOKEN_TG_BOT, None)
#    await bt.run()


# asyncio.run(main())
