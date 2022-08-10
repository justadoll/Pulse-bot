from aiohttp import ClientSession
from icmplib import async_ping
from icmplib.exceptions import NameLookupError
from asyncio import sleep
from loguru import logger
from json import loads

async def requester(method:str, host:str, nodes:int=5) -> dict:
    """
    Ping the server to see if it's alive.
    """
    h = {"Accept": "application/json"}
    async with ClientSession() as session:
        async with session.get(f"https://check-host.net/check-{method}?host={host}&max_nodes={nodes}", headers=h, verify_ssl=False) as response:
            text = await response.text()
            return loads(text)

async def count_checker(url:str, is_ping:bool) -> dict:
    url = url.replace("report","result")
    h = {"Accept": "application/json"}
    count = {}
    async with ClientSession() as session:
        async with session.get(url, headers=h, verify_ssl=False) as response:
            text = await response.text()
            json_data = loads(text)
        for node in json_data:
            count[node] = 0
            if json_data[node]:
                for i in json_data[node]:
                    if is_ping:
                        for x in i:
                            # logger.info(f"[+] PING: {node=} {x[0]}")
                            count[node] = count[node] + 1
                    else:
                        # logger.info(f"[+] HTTP: {node=} {i[0]}")
                        # if not ping
                        if i[0] == 1:
                            count[node] = count[node] + 1
            # else:
                # logger.warning(f"[-] {node} is down")
    return count

async def final_decision(hostname:str, results:list, active_counter:int, method:str, perm_link:str) -> str:
    actual_counter = 0
    final_str = f"<a href=\"{perm_link}\">{method.upper()}</a>\n\n"
    # logger.debug(f"{results=}")
    # logger.debug(f"{active_counter=}")
    for host in results:
        if results[host] >= 1:
            final_str += "🟢"
        else:
            final_str += "🔴"
        final_str += f"<code>{host}</code>\n"
        actual_counter += results[host]
    logger.info(f"{active_counter=} {actual_counter=}")
    if active_counter == actual_counter:
        logger.success(f"{hostname} is UP!")
        final_str += "Status: <b>UP</b>!\n\n"
        is_up = True
    elif actual_counter == 0:
        is_up = False
        own_ping_ok = await own_ping_check(hostname=hostname, count=5)
        logger.error(f"{hostname} is DOWN!")
        if own_ping_ok:
            logger.info(f"{hostname} bot-ping decided it's ALIVE")
            final_str += "🤖Bot-ping says it's <b>ALIVE</b>\n"
            is_up = True
        else:
            logger.warning(f"{hostname} bot-ping decided it's DEAD")
            final_str += "🤖Bot-ping says it's <b>DEAD</b>\n"
        final_str += "Status: <b>DOWN</b>!\n\n"
    else:
        logger.warning("Not all UP or DOWN!")
        final_str += "Status: <b>Not all UP or DOWN</b>!\n\n"
        is_up = True
    return (final_str, is_up)

async def checker(hostname:str, method:str, nodes:int):
    json_data = await requester(method=method, host=hostname, nodes=nodes)
    perm_link = json_data.get('permanent_link', None)
    logger.info(f"Perm link: {perm_link}")
    if perm_link:
        logger.debug("Sleeping...")
        await sleep(10)
        if method == "ping":
            active_counts = nodes * 4
            is_ping=True
        else:
            active_counts = nodes
            is_ping=False
        count_results = await count_checker(url=perm_link, is_ping=is_ping)
        results = await final_decision(hostname=hostname, results=count_results, active_counter=active_counts, method=method, perm_link=perm_link)
        return results

    else:
        logger.error(f"ERROR")

async def own_ping_check(hostname:str, count:int) -> bool:
    """ Sends ICMP packets to host from itself """
    try:
        res = await async_ping(hostname, count=count, interval=1, timeout=5, privileged=False)
    except NameLookupError:
        logger.warning(f"{hostname} dns lookup error")
    else:
        if res.packets_sent == res.packets_received:
            return True
        else:
            return False