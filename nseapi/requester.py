import os
from tkinter import N
from turtle import Turtle
from typing import Any, Type
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


class BaseApiAsync:
    SECTION_TRADEINFO = "trade_info"
    SECTION_CORPINFO = "corp_info"
    SEGMENT_CASH = 'favCapital'
    SEGMENT_DERIVATIVE = 'favDerivatives'
    SEGMENT_DEBT = 'favDebt'
    INSTRU_TYPE_FUT = 'FUTIDX'
    INSTRU_TYPE_OPT = 'OPTIDX'
    OPT_TYPE_CE = 'CE'
    OPT_TYPE_PE = 'PE'
    SERIES = ["AF", "BL", "EQ", "RL"]

    RETRY_INTERVAL = 0.5    # In seconds
    MAX_RETRY = 3
    TIMEOUT = 5

    def __init__(self, log_path: str = None) -> None:
        self.session = aiohttp.ClientSession(headers=c.HEADER_NSE)
        self.logger = get_logger('NseApiAsync', log_path)
        self.main_page_loaded = False

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
        if section != self.SECTION_CORPINFO and section != self.SECTION_TRADEINFO:
            raise TypeError(f"valid section: {self.SECTION_TRADEINFO} and {self.SECTION_CORPINFO}")

        return await self._get(url=c.URL_API + c.PATH_GET_QUOTE, params={'symbol': symbol.upper(), 'section': section}, request_name='quote')

    async def quote_derivative(self, symbol: str, identifier: str = None) -> dict:
        """
        quote about derivate

        Args:
            symbol (str): _description_
            identifier (str, optional): _description_. Defaults to None.

        Returns:
            dict: {
                "expiryDates": [str(dd-mmm-yyyy)],
                "filter": {expiryDate: "Invalid date", strikePrice: ""},
                "fut_timestamp": "21-Oct-2022 15:30:00",
                "info":{symbol: "NIFTY", companyName: "NIFTY", identifier: "none", activeSeries: [], debtSeries: [],…},
                "stocks":[
                    {
                        "marketDeptOrderBook": {totalBuyQuantity: 252650, totalSellQuantity: 627150,…},
                        "metadata":{instrumentType: "Index Options", expiryDate: "27-Oct-2022", optionType: "Call", strikePrice: 17600,…},
                        "underlyingValue": 17576.3,
                        "volumeFreezeQuantity": 2801
                    },
                    ......
                ],
                "strikePrices": [0, 0, 0, 7500, 8500, 8500, 8700, 9000, 9000, 9500, 9500, 9700, 9900, 10000, 10000, 10000, 10000,…],
                "underlyingValue: 17576.3,
                "vfq":2801
                }
        """
        return await self._get(url=c.URL_API + c.PATH_QUOTE_DERIVATIVE, params={'symbol': symbol.upper(), 'identifier': identifier}, request_name='quote_derivative')

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

    async def chart_data(self, symbol: str, index: bool, preopen: bool = False) -> dict:
        """
        1 sec chart data for symbol with timestamp and price only


        Args:
            symbol (str): TCSEQN
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
        params = {'index':  symbol.upper()}
        if index:
            params['indices'] = str(index).lower()
        else:
            params['index'] = params['index']+'EQN'

        if preopen:
            params['preopen'] = str(preopen).lower()
        return await self._get(url=c.URL_API + c.PATH_CHARTDATA_INDEX, params=params, request_name='chartdata_by_index')

    async def history_deri(self, symbol: str, identifier: str = None, from_date: str = None, to_date: str = None,
        option_type: str = None, strike_price: float = None, expiry_date: str= None, instrument_type: str = None) -> dict:
        """
        history data of derivative

        _extended_summary_

        Args:
            from_date (str): 23-09-2022
            to_date (str): 23-10-2022
            option_type (str): CE
            strike_price (float): 13950.00
            expiry_date (str): 27-Oct-2022
            instrument_type (str): OPTIDX
            symbol (str): NIFTY

        Returns:
            dict: {
                "data: [{_id: "6352990b5bacb48af147388a", FH_INSTRUMENT: "OPTIDX", FH_SYMBOL: "NIFTY",…},…],
                "meta": {symbol: "NIFTY", optionType: "CE", expiryDate: "27-Oct-2022", strikePrice: "13950.00",…}
            }
        """
        params = {'symbol': symbol}
        if identifier is not None:
            params['identifier'] = identifier

        if from_date is not None and to_date is not None:
            params['from'] = str(from_date)
            params['to'] = str(to_date)

        if option_type is not None:
            if option_type == self.OPT_TYPE_CE or option_type == self.OPT_TYPE_PE:
                params['optionType'] = option_type
            else:
                raise TypeError(f"option_type must be {self.OPT_TYPE_CE} or {self.OPT_TYPE_PE}")

        if strike_price is not None:
            params['strikePrice'] = float(strike_price)

        if expiry_date is not None:
            params['expiryDate'] = expiry_date

        if instrument_type is not None:
            if instrument_type == self.INSTRU_TYPE_OPT or instrument_type == self.INSTRU_TYPE_OPT:
                params['instrumentType'] = instrument_type
            else:
                raise TypeError(f"instrument_type must be {self.INSTRU_TYPE_FUT} or {self.INSTRU_TYPE_OPT}")

        return await self._get(url=c.URL_API + c.PATH_HISTORY_DERIVATIVES, params=params, request_name='history_deri')

    async def history_deri_meta(self, symbol: str, identifier: str = None) -> dict:
        """
        history data of derivative

        _extended_summary_

        Args:
            symbol (str): NIFTY
            indentifier (str): OPTIDXNIFTY27-10-2022CE13950.00

        Returns:
            dict: {
                "data": [["FUTIDX", "OPTIDX"], ["CE", "PE"],…],
                "from": "23-Sep-2022",
                "symbol": "NIFTY",
                "to": "23-Oct-2022",
                "years": {
                    2022: ["06-Oct-2022" "10-Nov-2022",…],…}
            }
        """
        return await self._get(url=c.URL_API + c.PATH_HISTORY_DERIVATIVES_META,
            params={'symbol': symbol, 'identifier': identifier}, request_name='history_deri_meta')

    async def history_equity(self, symbol: str, from_date: str = None, to_date: str = None,
        series: str = None) -> dict:
        """
        history data of equity

        Usage: history_equity('RELIANCE') # will receive last 1 month data

        Args:
            from_date (str): 23-09-2022
            to_date (str): 23-10-2022
            option_type (str): CE
            strike_price (float): 13950.00
            expiry_date (str): 27-Oct-2022
            instrument_type (str): OPTIDX
            symbol (str): NIFTY

        Returns:
            dict: {
                data:[{_id: "635289ffdd343400072e793e", CH_SYMBOL: "RELIANCE", CH_SERIES: "EQ", CH_MARKET_TYPE: "N",…},…]
                meta:{series: ["EQ"], fromDate: "24-10-2021", toDate: "24-10-2022", symbols: ["RELIANCE", "RELIANCE"]}
            }
        """
        params = {'symbol': symbol}

        if from_date is not None and to_date is not None:
            params['from'] = str(from_date)
            params['to'] = str(to_date)

        if isinstance(series, str) and series in self.SERIES:
            params['series'] = '"'+series+'"'

        return await self._get(url=c.URL_API + c.PATH_HIS_EQUITY, params=params, request_name='history_deri')

    async def bulkandblock(self, symbol: str, from_date: str = None, to_date: str = None) -> dict:
        """
        To get Bulk and Block deal for stock

        Args:
            symbol (str): RELIANCE
            from_date (str, optional): 24-10-2021. Defaults to None.
            to_date (str, optional): 24-10-2022. Defaults to None.

        Returns:
            dict: {
                data: [],
                meta: {series: ["EQ"], fromDate: "24-07-2022", toDate: "24-10-2022"}
            }
        """
        params = {'symbol': symbol}

        if from_date is not None and to_date is not None:
            params['from'] = str(from_date)
            params['to'] = str(to_date)

        return await self._get(url=c.URL_API + c.PATH_BULKBLOCK, params=params, request_name='buldandblock')

    async def high_low(self, symbol: str, year: str = None, month: str = None) -> dict:
        """
        Receive high low for given period of stock

        for 1 year from today leave year & month emplty
        year = will receive data about year
        month = receive data about year till month

        Args:
            symbol (str): Reliance
            year (str, optional): 2022. Defaults to None.
            month (str, optional): 10. Defaults to None.

        Returns:
            dict: {
                close: {_id: "635289ffdd343400072e793e", CH_TRADE_HIGH_PRICE: 2516.8, CH_TRADE_LOW_PRICE: 2467,…},
                from: "24-Oct-2021",
                high: 2817.35,
                low: 2311,
                open: {_id: "634fd611995e7700077f0d5a", CH_TRADE_HIGH_PRICE: 2655.2, CH_TRADE_LOW_PRICE: 2616.2,…},
                sumVal: 16491166.9924,
                sumVol: 6543.83903,
                thigh: {_id: "634fd6215176a10006904bcf", CH_TRADE_HIGH_PRICE: 2817.35, CH_TRADE_LOW_PRICE: 2742,…},
                tlow: {_id: "634fd80fb74c93000662eff0", CH_TRADE_HIGH_PRICE: 2402, CH_TRADE_LOW_PRICE: 2311,…},
                to: "24-Oct-2022",
                _id: "RELIANCE"
            }
        """
        
        params = {'symbol': symbol}

        if year is not None:
            params['year'] = str(year)

        if month is not None and year is not None:
            params['month'] = str(month)

        return await self._get(url=c.URL_API + c.PATH_HIGHLOW, params=params, request_name='buldandblock')

class BaseSymbolApiAsync(BaseApiAsync):
    
    def __init__(self,data: dict, log_path: str = None) -> None:
        super(BaseApiAsync, self).__init__(log_path = log_path)
        if 'symbol' in dict.keys():
            self.symbol = data['symbol']
            self.symbol_info = data['symbol_info']
            self.symbol_type = data['result_sub_type']
            self.active_series = data['activeSeries']

            if self.symbol_type == 'derivatives':
                self.__index = True
            elif self.symbol_type == 'equity':
                self.__index = False
        else:
            raise ValueError('data is not valid')

    async def option_chain(self) -> dict:
        """
        Get Option Chain Data
        
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
        return await super().option_chain(self.symbol, self.__index)

    async def meta_info(self) -> dict:
        """
        Info about symbol

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
        return await super().meta_info(self.symbol)

    async def quote(self, section: str=None, identifier: str = None) -> dict:
        """
        quote details about symbol

        Args:
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
        if self.symbol_type == 'equity':
            return await super().quote(self.symbol, section)
        elif self.symbol_type == 'derivatives':
            return await super().quote_derivative(self.symbol, identifier)

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
        if self.symbol_type == 'equity':
            return await super().corp_info(self.symbol)
        else:
            raise TypeError("Symbol is not equity")
    
    async def chart_data(self, preopen: False) -> dict:
        """
        chart data for symbol


        Args:
            preopen (False): Default False, True if want preopen data else False

        Returns:
            dict : {
                'identifier': str,
                'name', str symbol name,
                'grapthData': list[[timestamp, float]],
                'closePrice': float
            }
        """
        return await super().chart_data(self.symbol, self.__index, preopen)

    async def history_deri(self, identifier: str = None, from_date: str = None, to_date: str = None,
        option_type: str = None, strike_price: float = None, expiry_date: str= None, instrument_type: str = None) -> dict:
        """
        history data of derivative

        _extended_summary_

        Args:
            from_date (str): 23-09-2022
            to_date (str): 23-10-2022
            option_type (str): CE
            strike_price (float): 13950.00
            expiry_date (str): 27-Oct-2022
            instrument_type (str): OPTIDX
            symbol (str): NIFTY

        Returns:
            dict: {
                "data: [{_id: "6352990b5bacb48af147388a", FH_INSTRUMENT: "OPTIDX", FH_SYMBOL: "NIFTY",…},…],
                "meta": {symbol: "NIFTY", optionType: "CE", expiryDate: "27-Oct-2022", strikePrice: "13950.00",…}
            }
        """
        
        
        if self.symbol_type == 'derivatives':
            return await super().history_deri(self.symbol, identifier, from_date,to_date, option_type, strike_price, expiry_date,
            instrument_type)
        else:
            raise Type("Symbol is not derivative")

    async def history_deri_meta(self, identifier: str = None) -> dict:
        """
        history data of derivative

        _extended_summary_

        Args:
            symbol (str): NIFTY
            indentifier (str): OPTIDXNIFTY27-10-2022CE13950.00

        Returns:
            dict: {
                "data": [["FUTIDX", "OPTIDX"], ["CE", "PE"],…],
                "from": "23-Sep-2022",
                "symbol": "NIFTY",
                "to": "23-Oct-2022",
                "years": {
                    2022: ["06-Oct-2022" "10-Nov-2022",…],…}
            }
        """
        
        if self.symbol_type == 'derivatives':
            return await super().history_deri_meta(self.symbol, identifier)
        else:
            raise Type("Symbol is not derivative")

    async def history_equity(self, symbol: str, from_date: str = None, to_date: str = None,
        series: list = None) -> dict:
        """
        history data of equity

        Usage: history_equity('RELIANCE') # will receive last 1 month data

        Args:
            from_date (str): 23-09-2022
            to_date (str): 23-10-2022
            option_type (str): CE
            strike_price (float): 13950.00
            expiry_date (str): 27-Oct-2022
            instrument_type (str): OPTIDX
            symbol (str): NIFTY

        Returns:
            dict: {
                data:[{_id: "635289ffdd343400072e793e", CH_SYMBOL: "RELIANCE", CH_SERIES: "EQ", CH_MARKET_TYPE: "N",…},…]
                meta:{series: ["EQ"], fromDate: "24-10-2021", toDate: "24-10-2022", symbols: ["RELIANCE", "RELIANCE"]}
            }
        """
        
        if self.symbol_type == 'equity':
            return await super().history_equity(self.symbol, from_date, to_date, series)
        else:
            raise TypeError("Symbol is not equity")

    async def bulkandblock(self, from_date: str = None, to_date: str = None) -> dict:
        """
        To get Bulk and Block deal for stock

        Args:
            from_date (str, optional): 24-10-2021. Defaults to None.
            to_date (str, optional): 24-10-2022. Defaults to None.

        Returns:
            dict: {
                data: [],
                meta: {series: ["EQ"], fromDate: "24-07-2022", toDate: "24-10-2022"}
            }
        """
        return await super().bulkandblock(self.symbol, from_date, to_date)

    async def high_low(self, year: str = None, month: str = None) -> dict:
        """
        Receive high low for given period of stock

        for 1 year from today leave year & month emplty
        year = will receive data about year
        month = receive data about year till month

        Args:
            year (str, optional): 2022. Defaults to None.
            month (str, optional): 10. Defaults to None.

        Returns:
            dict: {
                close: {_id: "635289ffdd343400072e793e", CH_TRADE_HIGH_PRICE: 2516.8, CH_TRADE_LOW_PRICE: 2467,…},
                from: "24-Oct-2021",
                high: 2817.35,
                low: 2311,
                open: {_id: "634fd611995e7700077f0d5a", CH_TRADE_HIGH_PRICE: 2655.2, CH_TRADE_LOW_PRICE: 2616.2,…},
                sumVal: 16491166.9924,
                sumVol: 6543.83903,
                thigh: {_id: "634fd6215176a10006904bcf", CH_TRADE_HIGH_PRICE: 2817.35, CH_TRADE_LOW_PRICE: 2742,…},
                tlow: {_id: "634fd80fb74c93000662eff0", CH_TRADE_HIGH_PRICE: 2402, CH_TRADE_LOW_PRICE: 2311,…},
                to: "24-Oct-2022",
                _id: "RELIANCE"
            }
        """
        return await super().high_low(self.symbol, year, month)


class BaseNseApiAsync(BaseApiAsync):
    
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