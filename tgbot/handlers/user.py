from aiogram import Dispatcher
from aiogram.types import Message
from tgbot.services.check_host import requester, count_checker
from asyncio import sleep
from loguru import logger

from tgbot.models.users import User


async def user_start(message: Message, user: User):
    await message.reply("Hello, user!")
    json_data = await requester(method="ping", host="https://kpi.ua", nodes=20)
    perm_link = json_data.get('permanent_link', None)
    logger.info(f"Perm link: {perm_link}")
    if perm_link:
        logger.debug("Sleeping...")
        await sleep(5)
        count_results = await count_checker(url=perm_link, is_ping=True)
        for host in count_results:
            if count_results[host] >= 1:
                logger.info(f"[+] {host=} {count_results[host]=}")
            else:
                logger.warning(f"[-] {host=} {count_results[host]=}")
    else:
        logger.error(f"ERROR")


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
