import asyncio
from distutils.command.config import config
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.middlewares.db import DbMiddleware
from tgbot.services.database import create_db_session
from datetime import datetime 

from apscheduler.schedulers.background import BackgroundScheduler
from tgbot.services.bg_check_hosts import check_hosts

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def register_all_middlewares(dp):
    dp.setup_middleware(DbMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',

    )
    logger.info("Starting bot")
    config = load_config(".env")

    if config.tg_bot.use_redis:
        storage = RedisStorage()
    else:
        storage = MemoryStorage()

    global dp
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config
    bot['db'] = await create_db_session(config)

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


def tick():
    logging.info(f"Tick! The async time is {datetime.now()}")
    asyncio.run(check_hosts())

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    config = load_config(".env")
    scheduler.add_job(tick, 'interval', minutes=config.tg_bot.minutes_timeout)
    scheduler.start()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")