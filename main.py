from asyncio import run

from bots.father_bot import FatherBot
from bots.telegram.bot import TelegramBot
from database.module import DatabaseModule
from external.core_module import CoreModule
from declarative_data.datasets import SessionProviders

from config import settings

import asyncio

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def main():
    logger.info("Init core module..")
    core = CoreModule(host=settings.SERVER_IP, port=settings.SERVER_PORT)
    logger.info("Init database module..")
    dbm = DatabaseModule()
    logger.info("Init father bot..")
    father_bot = FatherBot(core, dbm, {})
    logger.info("Load sessions..")
    await father_bot.load_sessions()
    print(f"Loaded sessions:\n{father_bot.sessions}")
    core.bot = father_bot
    logger.info("Init telegram bot..")
    tg_bot = TelegramBot(settings.TOKEN_TG_BOT, father_bot)
    father_bot.bots[SessionProviders.telegram] = tg_bot
    logger.info("Runnig tasks..")
    tg_bot_task = tg_bot.run()
    http_task = core.run()
    logger.info("Success!")
    await asyncio.gather(http_task, tg_bot_task)

asyncio.run(main())