from requests import get as r_get
from tgbot.services.database import create_db_session
from tgbot.models.check_hosts import Hosts
from tgbot.services.check_host import checker

from tgbot.config import load_config

config = load_config(".env")

async def check_hosts():
    session = await create_db_session(config)
    hosts = await Hosts.get_all_hosts(session)
    for host in hosts:
        print(f"{host.hostname=} {host.last_change=}")
    
        http_result = await checker(hostname=host.hostname, method="http", nodes=25)
        ping_result = await checker(hostname=host.hostname, method="ping", nodes=20)

        response = r_get('https://api.telegram.org/bot' + config.tg_bot.token + '/sendMessage?chat_id=' + config.tg_bot.channel_id + '&text=' + http_result + ping_result + "&parse_mode=html")
        response_content = response.content
        print(f"{response_content=}")