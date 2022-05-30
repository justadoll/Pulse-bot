from aiogram import Dispatcher
from aiogram.types import Message
from tgbot.services.check_host import requester, count_checker
from asyncio import sleep
from loguru import logger

from tgbot.models.users import User


async def user_start(message: Message, user: User):
    await message.reply("Hello, user!")


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
