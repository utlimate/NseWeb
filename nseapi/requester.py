import os
from turtle import Turtle
from typing import Any
from urllib.parse import urljoin
import json
import pickle
import threading
import aiohttp
import nseapi.constant as c
from nseapi.logger import get_logger
from nseapi.data_models import IndexStocks, OptionChain
import time as t
import asyncio
from nseapi.generic import validate_directory, validate_status, AsyncLoopThread
import logging as _logging
import collections


def gen_cookie_from_main_page(res):
    cookies = {}
    for cookie in res.headers['Set-Cookie'].split(';'):
        if 'nseappid' in cookie:
            cookie = cookie.split(',')[1]
            cookie = cookie.split('=')
            cookies['nseappid'] = cookie[1]

        if 'nsit' in cookie:
            cookies['nsit'] = cookie.split('=')[1]

        if 'bm_mi' in cookie:
            cookie = cookie.split(',')[1]
            cookie = cookie.split('=')
            cookies['bm_mi'] = cookie[1]
    return cookies


def validate_res(res):
    if res.status_code == 200:
        return True
    else:
        return False


class NseApi:
    RETRY_INTERVAL = 0.5    # In seconds
    MAX_RETRY = 3
    TIMEOUT = 10

    def __init__(self, debug: bool=False, log_path=None, cache: bool = False):
        """ NSE website scrapper

        Args:
            debug (bool, optional): True will log. Defaults to False.
            save_path ([type], optional): path to save log report. Defaults to None.
            cache (bool, optional): save cookies. Defaults to False.
        """
        self._internet_connectivity = False
        self.__cache = cache
        self.__cache_path = None
        self._loop = asyncio.get_event_loop()
        self._loop_thread = threading.Thread(target = self._loop.run_forever, daemon=True, name="asyncio_loop")
        self.logger = get_logger('NseApi', log_path)
        self._request_dir = {}
        if not debug:
            self.logger.setLevel(_logging.WARNING)
        self.symbols_details = IndexStocks()
        self.session = aiohttp.Session(headers=c.HEADER)
        self.main_page_loaded = False
        self._validate_directories()
        self.init()

    def option_chain(self, symbol: str, index: bool):
        """ Return OptionChain Data for symobl

        Args:
            symbol (str): symbol of stock or index
            index (bool): True if symbol is index else False

        Returns:
            [pandas.DataFrame]:
        """
        params = {'symbol': symbol.upper()}
        try:
            res = None
            if index:
                res = self._get(c.URL_INDICES, params, 'Open Interest')
            else:
                res = self._get(c.URL_EQUITIES, params, 'Open Interest')

            if res is None:
                return None
            else:
                return OptionChain(res)
        except KeyError as e:
            self.logger.exception('Symbol: {} has error:'.format(symbol), exc_info=True)

    def index_stocks(self, indices_symbols: list):
        """ Return combine list of stocks for indices stocks
        :param indices_symbols: (str): name of index like NIFTY, BANKNIFTY
        :return: IndexStocks
        """
        self.logger.info('Requesting stock list of Index')

        none_result = set()
        for i in indices_symbols:
            i = c.INDICES_TO_NAME[i.upper()]
            params = {'index': i}
            res = self._get(c.URL_STOCK_LIST, params=params, request_name='Stock List')
            if res is not None:
                self.symbols_details.add_data(res)
            else:
                self.logger.error(f'Indices: {i} has none response')
                none_result.add(res)
        if len(none_result) > 0:
            self.logger.error(f"indices: {str(indices_symbols)} has one or more than none response")
            return None
        else:
            return self.symbols_details

    def init(self):
        """ this will load main page of nse website
        """
        try:
            self._loop_thread.start()



            res = self.session.get(c.URL_MAIN, timeout=self.TIMEOUT)
            if validate_res(res):
                self.main_page_loaded = True
                
                # Save cookies
                if self.__cache:
                    with open(self.__cache_path, 'wb') as f:
                        pickle.dump(self.session.cookies, f)
                self.logger.debug('Main Page - loaded')
            else:
                self.logger.error(f'Main Page - loading Failed - Not valid response, Status Code: {res.status_code}')
        except self.REQUEST_EXCEPTION as e:
            self.logger.error(f'Main Page - Network error in load Main Page')
        except Exception:
            self.logger.exception('Main page - has an error', exc_info=True)

    async def main_page(self):
        """ Load main page """

        res = await self.session.get(c.URL_MAIN)
        if validate_status(res):
            self.main_page_loaded = True
            return True
        else:
            return False
        
    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        res_data = None
        for i in range(1, self.MAX_RETRY + 1):
            self.logger.debug(f'{request_name} - Sending Request - Try: {i} - params: {str(params)}')

            try:
                if self.main_page_loaded:
                    res = self.session.get(url, params=params, timeout=timeout)
                    if validate_res(res):
                        self.logger.debug(f'{request_name} - Response Received {str(params)}')
                        return res.json()
                    else:
                        self.logger.error(f'{request_name}: Not Validate Response, Status Code: {res.status_code}')
                        t.sleep(self.RETRY_INTERVAL)
                        self.main_page_loaded = False
                        self.init()
                else:
                    self.logger.error('Main Page still not loaded. Load Main Page First')
                    self.init()

            except self.REQUEST_EXCEPTION as rc:
                self.logger.error(f'{request_name}: has network error')
                break
            except json.decoder.JSONDecodeError as e:
                self.logger.exception(f'{request_name}: Not Valid Json Data')
            except Exception as e:
                self.main_page_loaded = False
                t.sleep(self.RETRY_INTERVAL)
                self.init()
                self.logger.exception(f'Name:{request_name}, Params: {params}', exc_info=True)

        return res_data

    def _validate_directories(self):
        dir_path = c.HOME_DIR_PATH.joinpath('bin')
        validate_directory(dir_path)
        self.__cache_path = dir_path.joinpath('main_page_cookies.pickle')
    
    def _load_main_page_cookies(self):
        if self.__cache:
            try:
                self.logger.debug('loading cached cookies')
                with open(self.__cache_path, 'rb') as f:
                    self.session.cookies = pickle.load(f)
            except FileNotFoundError:
                self.init()

    def shutdown(self):
        self._loop.call_soon_threadsafe(self.session.close())
        self._loop.call_soon_threadsafe(self._loop.stop())
        return True

class NseApiAsync:
    SECTION_TRADEINFO = "trade_info"
    SECTION_CORPINFO = "corp_info"
    SEGMENT_CASH = 'favCapital'
    SEGMENT_DERIVATIVE = 'favDerivatives'
    SEGMENT_DEBT = 'favDebt'

    RETRY_INTERVAL = 0.5    # In seconds
    MAX_RETRY = 3
    TIMEOUT = 4

    def __init__(self, log_path: str = None) -> None:
        self.session = aiohttp.ClientSession(headers=c.HEADER_NSE)
        self.logger = get_logger('NseApiAsync', log_path)
        self.main_page_loaded = False

    async def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        res_data = None
        tryNo = 1
        while True:
        # for i in range(1, self.MAX_RETRY + 1):
            self.logger.debug(f'{request_name} - Sending Request - Try: {tryNo} - params: {str(params)}')

            try:
                res = await self.session.get(url, params=params, timeout=timeout)
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

    async def option_chain(self, symbol: str, index: bool) -> dict:
        """
        option_chain Get Option Chain Data

        Args:
            symbol (str): like NIFTY
            index (bool): True if symbol is index or False
        
        Returns:
            dict: {
                'records': {
                    'expiryDates': [str(dd-mmm-yyyy)],
                    'data': [
                        {'strikePrice': 7500,
                            'expiryDate': '29-Dec-2022',
                            'PE': {'strikePrice': 7500,
                            'expiryDate': '29-Dec-2022',
                            'underlying': 'NIFTY',
                            'identifier': 'OPTIDXNIFTY29-12-2022PE7500.00',
                            'openInterest': 53,
                            'changeinOpenInterest': 0,
                            'pchangeinOpenInterest': 0,
                            'totalTradedVolume': 0,
                            'impliedVolatility': 0,
                            'lastPrice': 3.05,
                            'change': 0,
                            'pChange': 0,
                            'totalBuyQuantity': 1950,
                            'totalSellQuantity': 0,
                            'bidQty': 750,
                            'bidprice': 0.8,
                            'askQty': 0,
                            'askPrice': 0,
                            'underlyingValue': 17576.3},
                            .......
                    ]
                    , 'timestamp': '21-Oct-2022 15:30:00',
                    'underlyingValue': 17576.3,
                    'strikePrices': [float]
                },
                'filtered'
            }
        """
        url = None

        if index:
            url = c.URL_API + c.PATH_OI_INDICES
        else:
            url = c.URL_API + c.PATH_OI_EQUITIES

        return await self._get(url, {'symbol': symbol.upper()}, 'option_chain')

    async def master(self) -> list:
        """
        master get all symbol list

        Returns:
            list: [ABB, INFY, ....]
        """
        return await self._get(c.URL_API + c.PATH_MASTER, request_name='master')

    async def daily_report(self, segment: str) -> list:
        """
        Daily report for all segment

        Args:
            segment (str): 'favCapital' - for capital market,
                            'favDerivatives' - for derivative market,
                            'favDebt' - for debt market

        Returns:
            list: [
                {
                    {'name': 'CM - Bhavcopy(csv)',
                    'type': 'daily-reports',
                    'category': 'capital-market',
                    'section': 'equities',
                    'link': 'https://archives.nseindia.com/content/historical/EQUITIES/2022/OCT/cm21OCT2022bhav.csv.zip'}
                },
                .....
            ]
        """
        return await self._get(c.URL_API + c.PATH_DAILY_REPORT, params={'key': segment}, request_name='daily_report')

    async def market_turnover(self) -> dict:
        """
        Return market turnover for all segment

        Returns:
            dict: {
                'data': [
                    {'name': 'Equities',
                    'yesterday': {'volume': 2658655723,
                    'value': 481923521629.25,
                    'openInterest': 0},
                    'today': {'volume': 2319869532,
                            'value': 541997832380.4605,
                            'oivalue': None,
                            'date': '21-Oct-2022 15:30:00'}
                    },
                    .....
                ],
                'derivativeToCashRatio': "4.82",
                'maxDate': "21-Oct-2022 23:14:02"
            }
        """
        return await self._get(c.URL_API + c.PATH_TURNOVER, request_name='market_turnover')

    async def search(self, symbol: str) -> dict:
        """
        search stock

        Args:
            symbol (str): INFY

        Returns:
            dict: {
                "marketState":[
                    {'market': 'Capital Market',
                    'marketStatus': 'Close',
                    'tradeDate': '24-Oct-2022',
                    'index': 'NIFTY 50',
                    'last': 17576.3,
                    'variation': 12.349999999998545,
                    'percentChange': 0.07,
                    'marketStatusMessage': 'Market is Closed'},
                    ......
                ]
            }
        """
        return await self._get(url=c.URL_API + c.PATH_SEARCH, params={'q': symbol}, request_name='search')

    async def meta_info(self, symbol: str) -> dict:
        """
        Info about symbol

        Args:
            symbol (str): "INFY"

        Returns:
            dict: data = {
                "symbol":"INFY",
                "companyName":
                "Infosys Limited",
                "industry":"COMPUTERS - SOFTWARE",
                "activeSeries":["EQ"],
                "debtSeries":[],
                "isin":"INE009A01021"}
        """
        return await self._get(url=c.URL_API + c.PATH_META_INFO, params={'symbol': symbol.upper()}, request_name='meta_info')

    async def quote(self, symbol: str, section="") -> dict:
        """
        quote details about symbol

        Args:
            symbol (str): INFY
            section (str, optional): it can be empty, Defaults to 'trade_info'.
                valid section: 'trade_info', 'corp_info'. 

        Returns:
            # empty
            dict: {
                'info': dict,
                'metadata': dict,
                'securityInfo': dict,
                'priceInfo': dict,
                'industryInfo': dict,
                'preOpenMarket'
            }

            #trade_info
            dict: {
                'noBlockDeals': bool,
                'bulkBlockDeals': list,
                'marketDeptOrderBook': dict,
                'securityWiseDP': dict,
            }
        """
        if section != self.SECTION_CORPINFO or section != self.SECTION_TRADEINFO:
            raise TypeError(f"valid section: {self.SECTION_TRADEINFO} and {self.SECTION_CORPINFO}")

        return await self._get(url=c.URL_API + c.PATH_GET_QUOTE, params={'symbol': symbol.upper(), 'section': section}, request_name='quote')

    async def corp_info(self, symbol) -> dict:
        """
        corp_info about symbol

        Args:
            symbol (_type_): _description_

        Returns:
            dict: {'corporate':{
                        'announcements':[dictionery],
                        'annualReport':[dictionery],
                        'boardMeetings':[dictionery],
                        'companyDirectory:[dictionery],
                        'corpEncumbrance':[dictionery],
                        'corporateActions':[dictionery],
                        'dailyBuyBack':[dictionery],
                        'financialResults':[dictionery],
                        'governance':[dictionery],
                        'insiderTrading':[dictionery],
                        'investorComplaints':[dictionery],
                        'pledgedetails':[dictionery],
                        'sastRegulations_29':[dictionery],
                        'sastRegulations_3132Post':[dictionery],
                        'secretarialCamp':[dictionery],
                        'shareholdingPatterns':[dictionery],
                        'transferAgentDetail':[dictionery],
                        'votingResults':[dictionery],
        """
        return await self._get(url=c.URL_API + c.PATH_GET_QUOTE, params={'symbol': symbol.upper(), 'section':'corp_info'}, request_name='get_quote')

    async def chart_data(self, symbol: str, index: bool, preopen: False) -> dict:
        """
        chart data for symbol


        Args:
            symbol (str): INFY
            index (bool): True if symbol is index else False
            preopen (False): Default False, True if want preopen data else False

        Returns:
            dict : {
                'identifier': str,
                'name', str symbol name,
                'grapthData': list[[timestamp, float]],
                'closePrice': float
            }
        """
        return await self._get(url=c.URL_API + c.PATH_CHARTDATA_INDEX, params={'symbol': symbol.upper(), "indices":index, "preopen": preopen}, request_name='chartdata_by_index')

    async def market_status(self) -> dict:
        """
        market_status for all segment

        Returns:
            dict: {
                'marketState': [{'market': 'Capital Market',
                                'marketStatus': 'Close',
                                'tradeDate': '24-Oct-2022',
                                'index': 'NIFTY 50',
                                'last': 17576.3,
                                'variation': 12.349999999998545,
                                'percentChange': 0.07,
                                'marketStatusMessage': 'Market is Closed'},
                                ......
                                ]
            }
        """
        return await self._get(url=c.URL_API + c.PATH_MARKETSTATUS, params=None, request_name='market_status')

class Ticker():
    def __init__(self, *args, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)