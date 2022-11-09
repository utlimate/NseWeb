import asyncio
from datetime import datetime
import threading
from scrapper.nseapi import NseApiAsync
from scrapper.nseapi.generic import AsyncLoopThread

def print_result(fut):
    print(f"Future is done: {fut.done()}")


loop = asyncio.get_event_loop()
nse = NseApiAsync()
init = loop.create_task(nse.init())
# nse.MAX_RETRY = 1

symbols = ['NIFTY', 'BANKNIFTY']


task_main = loop.create_task(nse.main())
# task_main = loop.create_task(nse.main())
# loop.run_until_complete(task_main)

# asyncio.gather(init, task_main)
loop.run_until_complete([init, task_main])

# start = datetime.now()

# for smb in symbols:
#     tasks.append(
#         loop.create_task(nse.option_chain(smb, index=True))
#     )

# loop.run_until_complete(*tasks)

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
# loop.run_until_complete(loop.shutdown_asyncgens)
# # loop_thread.stop()

# print("Loop Closed")

# # loop_thread.join()

# print("Thread Finished")
