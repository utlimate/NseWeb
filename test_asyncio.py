import threading
from unittest import result
import aiohttp
import asyncio


HEADER_NSE = {
    'accept-language': 'en-GB;q=0.5',
    'cache-control': 'no-cache',
    'sec-fetch-dest': 'document',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
}


URL_NSE = 'https://www.nseindia.com'
URL_GOOGLE = 'https://www.google.co.in'
URL_OC = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
URL_OC1 = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
URL_TURNOVER = 'https://www.nseindia.com/api/market-turnover'


session = aiohttp.ClientSession(headers=HEADER_NSE)


async def load_main():
    print("Loading Home Page")
    # Load Home Page
    result = None
    async with session.get(URL_NSE) as resp:
        result = await resp.text()
    
    print("Home Page loaded")



async def get_oi(url):
    print("Getting OI")
    oi = None
    async with session.get(url=url) as resp:
        oi = await resp.json()
    print("finished OI")

    return oi


async def turn_over():
    print("Getting Turn Over")
    oi = None
    async with session.get(url=URL_TURNOVER) as resp:
        if resp.status == 200:        
            oi = await resp.json()
            print(f"Turnover :{oi}")
    print("finished Finished Turn Over")

    return oi


loop = asyncio.get_event_loop()
# loop.run_until_complete(main())

futs = []

loop_thread = threading.Thread(target = loop.run_forever, daemon=True)
loop_thread.start()

task_main = loop.create_task(load_main())


while not task_main.done():
    pass

# Option Interest
futs.append(
        asyncio.run_coroutine_threadsafe(get_oi(URL_OC), loop=loop)
    )

futs.append(
    asyncio.run_coroutine_threadsafe(get_oi(URL_OC1), loop=loop)
)

futs.append(
    asyncio.run_coroutine_threadsafe(turn_over(), loop=loop)
)
# task_oi = [loop.create_task(get_oi(URL_OC), loop.create_task(URL_OC1))]
# results = await asyncio.gather(*task_oi)

print("Check futs status")
while len(futs) > 0:
    for f in futs:
        if f.done():
            futs.remove(f)
            # print("Fut remove")

print(len(futs))

# loop.call_soon_threadsafe(loop.stop)
# loop_thread.join()
print("Thread Finished")
task_main = loop.create_task(session.close())