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
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        # asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop())


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
    TIMEOUT = 0

    def __init__(self, log_path: str = None, parent = None) -> None:
        if parent is None:
            self.session = aiohttp.ClientSession(headers=c.HEADER_NSE)
            self.main_page_loaded = False
        else:
            self.session = parent.session
            self.main_page_loaded = parent.main_page_loaded
        
        self.logger = get_logger(self.__class__.__name__, log_path)

    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        self.logger.debug(f'{request_name} - Sending Request - params: {str(params)}')
    
        try:
            # Loading main page is not loaded
            if not self.main_page_loaded:
                await self.main()

            return await self.session.get(url, params=params, timeout=timeout)
        except Exception as e:
            self.logger.exception(f'Name:{request_name}, Params: {params}', exc_info=True)
            raise e

    async def main(self):
        """ Loading Main Page """
        self.logger.debug("Loading Main Page")
        res = await self.session.get(c.URL_MAIN)
        if validate_status(res):
            self.main_page_loaded = True
            self.logger.debug("Loading Main Page Successfull")
            return True
        else:
            self.logger.error(f"Loading Main Page Unsuccessful: Status Code - {res.status}")
            return False


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