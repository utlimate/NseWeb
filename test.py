import asyncio
import threading
from nseapi import NseApiAsync


nse = NseApiAsync()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(nse.main())
# print(loop.run_until_complete(nse.market_turnover()))


loop = asyncio.get_event_loop()
# loop.run_until_complete(main())

futs = []

loop_thread = threading.Thread(target = loop.run_forever, daemon=True)
loop_thread.start()

task_main = loop.create_task(nse.main())


while not task_main.done():
    pass

# Option Interest
futs.append(
        asyncio.run_coroutine_threadsafe(nse.market_turnover(), loop=loop)
    )

# futs.append(
#     asyncio.run_coroutine_threadsafe(get_oi(URL_OC1), loop=loop)
# )

# futs.append(
#     asyncio.run_coroutine_threadsafe(turn_over(), loop=loop)
# )
# task_oi = [loop.create_task(get_oi(URL_OC), loop.create_task(URL_OC1))]
# results = await asyncio.gather(*task_oi)

print("Check futs status")
while len(futs) > 0:
    for f in futs:
        if f.done():
            print(f.result())
            futs.remove(f)
            # print("Fut remove")

print(len(futs))

# loop.call_soon_threadsafe(loop.stop)
# loop_thread.join()
print("Thread Finished")
task_main = loop.create_task(nse.session.close())