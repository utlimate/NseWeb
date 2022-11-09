import asyncio
from datetime import datetime
import threading
from scrapper.nseapi import NseApiAsync, NseApi
from scrapper.nseapi.generic import AsyncLoopThread

def print_result(fut):
    print(f"Future is done: {fut.done()}")

symbols = {
    'NIFTY': True,
    "BANKnity": True,
    'reliance': False,
    'infy': False,
    'sbin': False,
    'finnify': True,
    'adanient': False,
    'DIVISLAB': False,
    'TATASTEEL': False,
    'ACC': False,
    'DIXON': False
}

nse = NseApi()
nse.init()

oi = nse.option_chain(symbols)
nse.shutdown()
print('Complete')
# nse = NseApiAsync()
# # nse.MAX_RETRY = 1

# tasks = []

# # loop = asyncio.get_event_loop()
# # loop_thread = threading.Thread(target = loop.run_forever, daemon=True)
# loop_thread = AsyncLoopThread()
# loop = loop_thread.loop
# loop_thread.start()

# task_init = asyncio.run_coroutine_threadsafe(nse.init(), loop=loop)
# task_main = asyncio.run_coroutine_threadsafe(nse.main(), loop=loop)


# while not task_main.done():
#     pass

# start = datetime.now()

# for smb, index_status in symbols.items():
#     tasks.append(
#         asyncio.run_coroutine_threadsafe(
#             nse.option_chain(smb, index=index_status), loop=loop)
#     )

# # for t in tasks:
# #     t.add_done_callback(print_result)

# while True:
#     unfinished = [t for t in tasks if not t.done()]

#     if len(unfinished) < 1:
#         break
#     del unfinished

# duration = datetime.now() - start

# print(f"Total minutes for scarpping : {duration.total_seconds()/60}")

# task_close = asyncio.run_coroutine_threadsafe(nse.close(), loop=loop)
# while not nse.session.closed or not task_close.done():
#     pass

# print(f"Session close: {nse.session.closed}")
# loop_thread.stop()

# print("Loop Closed")

# loop_thread.join()

# print("Thread Finished")
