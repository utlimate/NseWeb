import scrapper
from scrapper.nseapi.requester import BaseNseApiAsync
from scrapper.nseapi.requester import BaseSymbolApiAsync
import scrapper.nseapi.constant as _c
from pathlib import Path as _Path
from datetime import datetime as _datetime
import asyncio
from .financial.requester import FinApiAsync

_c.HOME_DIR_PATH = _Path(__file__).parent
_c.TODAY_DATE = _datetime.now()
__version__ = scrapper.__version__


class NseApiAsync(BaseNseApiAsync):
    TIMEOUT = 4

    def __init__(self, log_path: str = None, max_retry: int = None) -> None:
        super().__init__(log_path, max_retry)
        self.finance = FinApiAsync(self, max_retry)

    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        res_data = None
        tryNo = 1
        while True:
            self.logger.debug(f'{request_name} - Sending Request - Try: {tryNo} - params: {str(params)}')

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
            
            if tryNo >= self.MAX_RETRY and self.MAX_RETRY > 0:
                raise RuntimeError(f"Maximum retry exhausted")

            tryNo += 1
    
        return res_data


class SymbolApiAsync(BaseSymbolApiAsync):
    TIMEOUT = 4

    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        res_data = None
        tryNo = 1
        while True:
        # for i in range(1, self.MAX_RETRY + 1):
            self.logger.debug(f'{request_name} - Sending Request - Try: {tryNo} - params: {str(params)}')

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
            
            if tryNo >= self.MAX_RETRY and self.MAX_RETRY > 0:
                raise RuntimeError(f"Maximum retry exhausted")

            tryNo += 1
    
        return res_data
