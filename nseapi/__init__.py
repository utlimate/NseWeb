from nseapi.requester import BaseNseApiAsync as _BaseNseApiAsync
from nseapi.requester import BaseSymbolApiAsync as _BaseSymbolApiAsync
import nseapi.constant as _c
from pathlib import Path as _Path
from datetime import datetime as _datetime

_c.HOME_DIR_PATH = _Path(__file__).parent
_c.TODAY_DATE = _datetime.now()
__version__ = '0.0.12'


class NseApiAsync(_BaseNseApiAsync):
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
                t.sleep(self.RETRY_INTERVAL)
            
            tryNo += 1
    
        return res_data


class SymbolApiAsync(_BaseSymbolApiAsync):
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
                t.sleep(self.RETRY_INTERVAL)
            
            tryNo += 1
    
        return res_data
