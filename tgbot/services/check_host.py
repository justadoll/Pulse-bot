from aiohttp import ClientSession
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
            else:
                logger.warning(f"[-] {node} is down")
    return count
