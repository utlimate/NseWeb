import asyncio
import os
from threading import Thread

def validate_directory(dir_path: str):
    """ This will create new directory if not exist """

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    return True


def validate_status(res):
    if res.status == 200:
        return True
    else:
        return False


class AsyncLoopThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop())