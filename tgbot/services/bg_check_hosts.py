from requests import get as r_get
from json import loads
from tgbot.services.database import create_db_session
from tgbot.models.check_hosts import Hosts
from tgbot.services.check_host import checker

from tgbot.config import load_config

config = load_config(".env")

async def check_hosts():
    session = await create_db_session(config)
    hosts = await Hosts.get_all_hosts(session)
    for host in hosts:
    
        http_result, http_is_up = await checker(hostname=host.hostname, method="http", nodes=25)
        ping_result, ping_is_up = await checker(hostname=host.hostname, method="ping", nodes=20)
    
        if http_is_up != host.http_up:
            print(f"[+] HTTP Status CHANGED! {http_is_up=} {host.http_up=}")
            http_changer = f"<b>{host.hostname} changed status!</b>\n"
            http_result = f"{http_changer}{http_result}"
            await Hosts.edit_host_status(session_maker=session, host_id=host.id, http_up=http_is_up, ping_up=ping_is_up)
            response = r_get('https://api.telegram.org/bot' + config.tg_bot.token + '/sendMessage?chat_id=' + str(config.tg_bot.channel_id) + '&text=' + http_result + "&parse_mode=html")
            http_msg = loads(response.content.decode('utf-8'))
            msg_id = http_msg['result']['message_id']
            chat_id = http_msg['result']['chat']['id']
            print(f"{type(msg_id)=} {msg_id} {type(chat_id)=} {chat_id=}")
        if ping_is_up != host.ping_up:
            print(f"[+] PING Status CHANGED! {ping_is_up=} {host.ping_up=}")
            ping_changer = f"<b>{host.hostname} changed status!</b>\n"
            ping_result = f"{ping_changer}{ping_result}"
            await Hosts.edit_host_status(session_maker=session, host_id=host.id, http_up=http_is_up, ping_up=ping_is_up)
            try:
                if http_msg:
                    response = r_get('https://api.telegram.org/bot' + config.tg_bot.token + '/editMessageText?chat_id=' + str(chat_id) + "&message_id=" + str(msg_id) + '&text=' + http_result+ping_result + "&parse_mode=html")
                    # print(f"{response.content=}")
            except UnboundLocalError:
                response = r_get('https://api.telegram.org/bot' + config.tg_bot.token + '/sendMessage?chat_id=' + str(config.tg_bot.channel_id) + '&text=' + ping_result + "&parse_mode=html")
            
        else:
            print(f"[-] Status NOT changed! {http_is_up=} {host.http_up=}\n {ping_is_up=} {host.ping_up=}")
            