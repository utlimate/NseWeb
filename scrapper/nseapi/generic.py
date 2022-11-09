import asyncio
import os
from threading import Thread
import logging as _logging
import sys, os
from datetime import datetime as _datetime
from typing import Union
from pathlib import Path as _Path
import aiohttp
from . import constant as c


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
    """
    AsyncLoopThread Thread for event looop

    _extended_summary_

    Args:
        Thread : threading.Thread
    """
    def __init__(self, set_default_loop: bool = False):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()
        if set_default_loop:
            asyncio.set_event_loop(self.loop)

    def run(self):
        """
        run the thread
        """
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()


def get_logger(name: str, log_dir: Union[_Path, str]=None) -> _logging.Logger:
    """ Return Logger Object

    Args:
        name (str): name of logger
        log_dir (Union[_Path, str], optional): path of logger. Defaults to None.

    Returns:
        [logging.Logger]: logging.Logger
    """

    # Create a custom logger
    logger = _logging.getLogger(name)

    now = _datetime.now()
    now_str = now.strftime("%d-%m-%Y")

    # Create handlers
    logger.setLevel(_logging.DEBUG)

    # Command line logger
    c_handler = _logging.StreamHandler(stream=sys.stdout)
    c_handler.setLevel(_logging.DEBUG)
    c_format = _logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%m-%y %I:%M:%S %p")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler
    if log_dir is not None:
        if isinstance(log_dir, str):
            log_dir = _Path(log_dir)

        if validate_directory(log_dir):
            file_name = log_dir.joinpath(name + '_' + now_str + '.log')
            f_handler = _logging.FileHandler(file_name)
            f_handler.setLevel(_logging.INFO)
            f_format = _logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%d-%m-%y %I:%M:%S %p")
            f_handler.setFormatter(f_format)
            logger.addHandler(f_handler)

    return logger


class BaseRequester:
    TIMEOUT = 0.2

    def __init__(self, loop: asyncio.windows_events.ProactorEventLoop = None, log_path: str = None, parent = None) -> None:
        # if parent is None:
        #     self.session = aiohttp.ClientSession(headers=c.HEADER_NSE)
        #     self.main_page_loaded = False
        # else:
        #     self.session = parent.session
        #     self.main_page_loaded = parent.main_page_loaded
        self.session = None
        self.main_page_loaded = False
        self._getting_main = False
        
        if loop is not None:
            loop.create_task(self.init())
        
        self.logger = get_logger(self.__class__.__name__, log_path)
        self._wait_for_main = asyncio.Event()
        self._wait_for_init = asyncio.Event()
        
    def _main_status_clear(self, req_name):
        self.logger.debug(f"{req_name}: Clearing Main Page: Clear")
        self.main_page_loaded = False
        self._wait_for_main.clear()
        
    def _main_status_set(self, req_name):
        self.logger.debug(f"{req_name}: Main Page Status: Set")
        self.main_page_loaded = True
        self._wait_for_main.set()
        
    async def init(self, parent = None):
        if parent is None:
            self.session = aiohttp.ClientSession(headers=c.HEADER_NSE)
            self.main_page_loaded = False
        else:
            self.session = parent.session
            self.main_page_loaded = parent.main_page_loaded
        self._wait_for_init.set()

    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        self.logger.debug(f'{request_name} - Sending Request - params: {str(params)}, wait for main')
    
        try:
            # Loading main page is not loaded
            if not self.main_page_loaded:
                await self.main()
            
            await self._wait_for_main.wait()        
            res = await self.session.get(url, params=params, timeout=timeout)
            self.logger.debug(f'{request_name} - Response Received - params: {str(params)}')
            return res
        except Exception as e:
            self._main_status_clear(request_name)
            self.logger.exception(f'Name: {request_name}, Params: {params}', exc_info=True)
            raise e

    async def main(self):
        """ Loading Main Page """
        self.logger.debug("Loading Main Page, wait for init")
        await self._wait_for_init.wait()
        
        if not self._getting_main:
            self._main_status_clear("Main Page")
            self._getting_main = True
            res = await self.session.get(c.URL_MAIN)
            self._getting_main = False
            if validate_status(res):
                self._main_status_set("Main Page")
                self.logger.debug("Loading Main Page Successfull")
                return True
            else:
                self.logger.error(f"Loading Main Page Unsuccessful: Status Code - {res.status}")
                await asyncio.sleep(self.TIMEOUT)
                await self.main()
        else:
            return self.main_page_loaded

    async def close(self):
        """
        close the seesion

        Returns:
            _type_: _description_
        """
        await self.session.close()

class MyObj(object):
    def __init__(self, *args, **kwargs):
        for a in args:
            if isinstance(a, str):
                self[a.replace("-", "_").replace(" ", "").lower()] = a

        for k , v in kwargs.items():
            if isinstance(k, str):
                self[k.replace(" ", "").lower()] = v

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)