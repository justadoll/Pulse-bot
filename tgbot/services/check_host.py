from aiohttp import ClientSession
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
                        if i[2] == "OK":
                            # logger.info(f"[+] HTTP: {node=} {i[2]}")
                            count[node] = count[node] + 1
            #else:
            #    logger.warning(f"[-] {node} is down")
    return count

def final_decision(hostname:str, results:list, active_counter:int, method:str) -> str:
    actual_counter = 0
    final_str = f"<b>{hostname}</b>\n<b>{method.upper()}</b>\n\n"
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
        logger.success("UP!")
        final_str += "Status: <b>UP</b>!\n\n"
    elif actual_counter == 0:
        logger.error("DOWN!")
        final_str += "Status: <b>DOWN</b>!\n\n"
    else:
        logger.warning("Not all UP or DOWN!")
        final_str += "Status: <b>Not all UP or DOWN</b>!\n\n"
    return final_str

async def checker(hostname:str, method:str, nodes:int):
    json_data = await requester(method=method, host=hostname, nodes=nodes)
    perm_link = json_data.get('permanent_link', None)
    logger.info(f"Perm link: {perm_link}")
    if perm_link:
        logger.debug("Sleeping...")
        await sleep(5)
        if method == "ping":
            active_counts = nodes * 4
            is_ping=True
        else:
            active_counts = nodes
            is_ping=False
        count_results = await count_checker(url=perm_link, is_ping=is_ping)
        return final_decision(hostname=hostname, results=count_results, active_counter=active_counts, method=method)

    else:
        logger.error(f"ERROR")