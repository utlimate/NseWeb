from pathlib import Path as _Path
from datetime import datetime as _datetime
import asyncio
from typing import Union
from scrapper.nseapi.generic import AsyncLoopThread
from scrapper.nseapi.requester import BaseNseApiAsync
from scrapper.nseapi.requester import BaseSymbolApiAsync
import scrapper.nseapi.constant as _c
from .financial.requester import FinApiAsync

_c.HOME_DIR_PATH = _Path(__file__).parent
_c.TODAY_DATE = _datetime.now()


class NseApiAsync(BaseNseApiAsync):
    """
    NseApiAsync Asyncio api for NSE website

    Args:
        BaseNseApiAsync (_type_): _description_

    Raises:
        RuntimeError: _description_
    """
    TIMEOUT = 4

    def __init__(self, log_path: str = None, max_retry: int = None) -> None:
        super().__init__(log_path, max_retry)
        self.finance = FinApiAsync(self, max_retry)

    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        res_data = None
        try_no = 1
        while True:
            if try_no > self.MAX_RETRY and self.MAX_RETRY > 0:
                raise RuntimeError("Maximum retry exhausted")
            self.logger.debug(
                f'{request_name} - Sending Request - Try: {try_no} - params: {str(params)}'
                )

            try:
                res = await super()._get(url, params, request_name)
                if res.ok:
                    self.logger.debug(f"{request_name} - Params: {params} - Response OK")
                    res_data = await res.json()
                    res.close()
                    break
                else:
                    self.logger.error(
                        f'{request_name}: Status Code: {res.status}')
                    # To avoid unauthorized error
                    if res.status == 401:
                        if not self.main_page_loaded:
                            await self.main()
                    # await asyncio.sleep(self.RETRY_INTERVAL)
            except Exception as e:
                self.logger.exception(
                    f'Name:{request_name}, Params: {params}', exc_info=True)
                await asyncio.sleep(self.RETRY_INTERVAL)
            try_no += 1
        return res_data


class SymbolApiAsync(BaseSymbolApiAsync):
    TIMEOUT = 4

    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        res_data = None
        try_no = 1
        while True:
            # for i in range(1, self.MAX_RETRY + 1):
            self.logger.debug(f'{request_name} - Sending Request - Try: {try_no} - params: {str(params)}')

            try:
                res = await super()._get(url, params, request_name, timeout)
                if res.ok:
                    self.logger.debug(f"{request_name}: Response Received")
                    res_data = await res.json()
                    res.close()
                    break
                else:
                    self.logger.error(f'{request_name}: Status Code: {res.status}')
                    # To avoid unauthorized error
                    if res.status == 401:
                        if not self.main_page_loaded:
                            await self.main()
                    # await asyncio.sleep(self.RETRY_INTERVAL)

            except Exception as e:
                self.logger.exception(f'Name:{request_name}, Params: {params}', exc_info=True)
                await asyncio.sleep(self.RETRY_INTERVAL)     
            if try_no >= self.MAX_RETRY and self.MAX_RETRY > 0:
                raise RuntimeError(f"Maximum retry exhausted")

            try_no += 1
        return res_data


class NseApi:
    def __init__(self, log_path: str = None, max_retry: int = None) -> None:
        self.loop_thread = AsyncLoopThread()
        self.loop = self.loop_thread.loop
        self.loop_thread.start()
        self.nse_async = NseApiAsync(log_path=log_path, max_retry=max_retry)
        
    def init(self):
        task_init = asyncio.run_coroutine_threadsafe(self.nse_async.init(), loop=self.loop)
        task_main = asyncio.run_coroutine_threadsafe(self.nse_async.main(), loop=self.loop)
        
    def __wait_for_finish(self, tasks: dict):
        while True:
            unfinished = [t for t in tasks.values() if not t.done()]
            if len(unfinished) < 1:
                break
            del unfinished
        return True
        
    def option_chain(self, symbols: dict) -> dict:
        for s, index_status in symbols.items():
            symbols[s] = asyncio.run_coroutine_threadsafe(
                self.nse_async.option_chain(s, index_status), self.loop
            )
        
        if self.__wait_for_finish(symbols):
            return {k: v.result() for k, v in symbols.items()}
        
    def shutdown(self):
        task_close = asyncio.run_coroutine_threadsafe(self.nse_async.close(), loop=self.loop)
        while not self.nse_async.session.closed or not task_close.done():
            pass

        print(f"Session close: {self.nse_async.session.closed}")
        self.loop_thread.stop()
        