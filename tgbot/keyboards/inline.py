from aiogram import types
from aiogram.utils.callback_data import CallbackData

admin_menu = CallbackData("admin_menu", "action")
hosts_cb = CallbackData("hosts_cb", "host_id", "action")

cancel_bt = types.InlineKeyboardButton('Отмена', callback_data=admin_menu.new(action='cancel'))

def get_admin_menu():
    kb = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Список хостов', callback_data=admin_menu.new(action='all_hosts')),
                    types.InlineKeyboardButton('Добавить хост', callback_data=admin_menu.new(action='add_host'))
    )
    return kb

def cancel_kb():
    return types.InlineKeyboardMarkup().row(cancel_bt)

def ok_kb():
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('ОK', callback_data=admin_menu.new(action='cancel')))

def check_new_host_rm(host_id:str):
    return types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Да!', callback_data=hosts_cb.new(action="check", host_id=host_id)),
            types.InlineKeyboardButton('Нет!', callback_data=admin_menu.new(action='cancel')))
    
def get_hosts(hosts:list):
    kb = types.InlineKeyboardMarkup()
    for host in hosts:
        kb.add(types.InlineKeyboardButton(host.hostname, callback_data=hosts_cb.new(host_id=host.id, action="get_host")))
    kb.add(cancel_bt)
    return kb
    
def del_hostname(id:str):
    kb = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('🛑Удалить хост', callback_data=hosts_cb.new(host_id=id, action="del_host")), cancel_bt)
    kb.add(types.InlineKeyboardButton('Проверить хост!', callback_data=hosts_cb.new(action="check", host_id=id)))
    return kb