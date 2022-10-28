import ast
import asyncio
from datetime import datetime
from os import link
import requests
from nseapi.generic import BaseRequester, MyObj, validate_status, AsyncLoopThread
from nseapi.requester import BaseApiAsync
import xml.etree.ElementTree as ET
import nseapi.constant as _cont


class BaseFinApiAsync(BaseRequester):
    PERIOD = MyObj(*['Annual', 'Half-Yearly', 'Quarterly', 'Others'])
    INDEX = MyObj(*['equities', 'sme', 'debt'])

    def __init__(self, parent:BaseApiAsync = None, max_retry: int = 0, log_path: str = None) -> None:

        if parent is not None:
            self.parent = parent
            self.logger = parent.logger
        else:
            super(BaseFinApiAsync, self).__init__(log_path)

        self.thread = AsyncLoopThread()
        if isinstance(max_retry, int):
            self.MAX_RETRY = max_retry

    async def results(self, index: str, symbol: str = None, period: str = None) -> dict:
        """
        Get result for symbol

        

        Args:
            index (str): valid index = ['equities', 'sme', 'debt']
            symbol (str, optional): INFY. Defaults to None.
            period (str, optional): valid period = ['Annual', 'Half-Yearly', 'Quarterly', 'Others']. Defaults to None.

        Raises:
            TypeError: if not valid index
            TypeError: if not valid period

        Returns:
            "<class 'aiohttp.client_reqrep.ClientResponse'>": response class
        """

        if isinstance(index, str):
            if index in self.INDEX:
                params = {'index': index}
            else:
                raise TypeError(f"index is not valid. It must be from {str(self.INDEX)}")

        if isinstance(symbol, str):
            params['symbol'] = symbol.upper()

        if isinstance(period, str):
            if period in self.PERIOD:
                params['period'] = period
            else:
                raise TypeError(f"period is not valid. It must be from {str(self.PERIOD)}")

        return await self._get(_cont.PATH_FIN_RESULTS, params=params, request_name='results')

    async def get_xml(self, xml_link: str):
        response = await self._get(xml_link, request_name='get_xml')
        return await response.text()

    async def get_link(self, data: list):
        links = []
        for d in data:
            if len(d['xbrl']) > len('https://archives.nseindia.com/corporate/xbrl/-'):
                links.append(d['xbrl'])
        return links

    async def parse_XML(self, xmltext):
        tree = ET.fromstring(xmltext)
        result = {}
        for item in tree.findall(".//*[@contextRef='OneD']"):
            if item.tag.startswith("{http://www.bseindia.com/xbrl/fin/2020-03-31/in-bse-fin}"):
                key = item.tag.replace("{http://www.bseindia.com/xbrl/fin/2020-03-31/in-bse-fin}", '')
                
                value = item.text
                try:
                    value = ast.literal_eval(value)
                except Exception as e:
                    try:
                        value = datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        if value == 'true' or value == 'false':
                            value = ast.literal_eval(value.title())

                result[key] = value
        
        return result


class FinApiAsync(BaseFinApiAsync):
    PERIOD = MyObj(*['Annual', 'Half-Yearly', 'Quarterly', 'Others'])
    INDEX = MyObj(*['equities', 'sme', 'debt'])
    TIMEOUT = 0

    async def results(self, index: str, symbol: str = None, period: str = None) -> dict:
        """
        Get result for symbol

        

        Args:
            index (str): valid index = ['equities', 'sme', 'debt']
            symbol (str, optional): INFY. Defaults to None.
            period (str, optional): valid period = ['Annual', 'Half-Yearly', 'Quarterly', 'Others']. Defaults to None.

        Raises:
            TypeError: if not valid index
            TypeError: if not valid period

        Returns:
            "<class 'aiohttp.client_reqrep.ClientResponse'>": response class
        """
        response = await super().results(index, symbol, period)
        
        if validate_status(response):
            data = await response.json()
            links = await self.get_link(data)
            get_xml_tasks = [self.get_xml(l) for l in links]
            results = await asyncio.gather(*get_xml_tasks)

            #parse xml
            parse_xml_tasks = [self.parse_XML(r) for r in results]
            results = await asyncio.gather(*parse_xml_tasks)
            return results
        else:
            raise ConnectionError(f"Not valid response, Status Code: {response.status}")
