from nseapi.requester import BaseNseApiAsync
import nseapi.constant as _c
from pathlib import Path as _Path
import os as _os
from datetime import datetime as _datetime

_c.HOME_DIR_PATH = _Path(__file__).parent
_c.TODAY_DATE = _datetime.now()
__version__ = '0.0.6'
__all__ = ['BaseNseApiAsync']


class _BaseNseApiAsync:
    SECTION_TRADEINFO = "trade_info"
    SECTION_CORPINFO = "corp_info"
    SEGMENT_CASH = 'favCapital'
    SEGMENT_DERIVATIVE = 'favDerivatives'
    SEGMENT_DEBT = 'favDebt'
    INSTRU_TYPE_FUT = 'FUTIDX'
    INSTRU_TYPE_OPT = 'OPTIDX'
    OPT_TYPE_CE = 'CE'
    OPT_TYPE_PE = 'PE'

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
        return await self._get(url=c.URL_API + c.PATH_HISTORY_DERIVATIVES, params={'symbol': symbol, 'identifier': identifier}, request_name='history_deri')

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
        return await self._get(url=c.URL_API + c.PATH_HISTORY_DERIVATIVES, params={'symbol': symbol, 'series': series, 'from': from_date, 'to':to_date}, request_name='history_deri')

