from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline import admin_menu, hosts_cb, get_admin_menu, cancel_kb, ok_kb, get_hosts, del_hostname
from tgbot.models.check_hosts import Hosts
from tgbot.misc.states import HostSt
import typing

# shit...
from tgbot.config import load_config
from tgbot.services.database import create_db_session

config = load_config(".env")

async def admin_start(message: Message):
    await message.reply("Hello, admin!", reply_markup=get_admin_menu())


async def admin_all_hosts(query: CallbackQuery, callback_data: typing.Dict[str, str]):
    await query.answer()
    session = await create_db_session(config)
    hosts = await Hosts.get_hosts(session, query.from_user.id)
    await query.message.edit_text("<b>Список ваших хостов:</b> ...", reply_markup=get_hosts(hosts))


async def get_unic_host(query: CallbackQuery, callback_data: typing.Dict[str, str]):
    await query.answer()
    session = await create_db_session(config)
    host = await Hosts.get_host(session, id=int(callback_data['host_id']))
    str_last_change = host[0].last_change.strftime("%d.%m.%Y %H:%M:%S")
    await query.message.edit_text(f"<b>Хостнейм:</b> <code>{host[0].hostname}</code>\n<b>Последняя активность:</b> <code>{str_last_change}</code>", reply_markup=del_hostname(callback_data['host_id']))


async def get_hostname(message: Message, state:FSMContext):
    try:
        session = await create_db_session(config)
        await Hosts.add_host(session, message.from_user.id, message.text)
    except Exception as e:
        await message.reply("<b>Что-то пошло не так...</b>")
    else:
        await message.reply("<b>Хост был успешно добавлен!</b>", reply_markup=ok_kb())
    await state.finish()


async def admin_add_host(query: CallbackQuery, callback_data: typing.Dict[str, str]):
    await query.answer()
    await query.message.edit_text("<b>Напишите айпи или доменное имя:</b>", reply_markup=cancel_kb())
    await HostSt.add_hostname.set()

async def admin_del_host(query: CallbackQuery, callback_data: typing.Dict[str, str]):
    await query.answer()
    session = await create_db_session(config)
    await Hosts.del_host(session, telegram_id=query.from_user.id, host_id=int(callback_data['host_id']))
    await query.message.edit_text("<b>Готово!</b>", reply_markup=ok_kb())

async def cancel(query: CallbackQuery, callback_data: typing.Dict[str, str], state:FSMContext):
    await query.answer()
    await state.finish()
    await query.message.edit_text("Hello, admin!", reply_markup=get_admin_menu())


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(admin_all_hosts, admin_menu.filter(action="all_hosts"), is_admin=True)
    dp.register_callback_query_handler(get_unic_host, hosts_cb.filter(action="get_host"), is_admin=True)
    dp.register_callback_query_handler(admin_del_host, hosts_cb.filter(action="del_host"), is_admin=True)
    
    dp.register_callback_query_handler(admin_add_host, admin_menu.filter(action="add_host"), is_admin=True)
    dp.register_message_handler(get_hostname, state=HostSt.add_hostname, is_admin=True)
    dp.register_callback_query_handler(cancel, admin_menu.filter(action="cancel"), state="*", is_admin=True)
