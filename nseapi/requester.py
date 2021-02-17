import pickle
import requests
from nseapi.logger import get_logger
import nseapi.constant as c
import time as t


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


class Nse:
    def __init__(self, log_info=None):
        self.logger = get_logger(__name__)
        self.log_info = log_info
        self.session = requests.Session()
        self.session.headers.update(c.HEADER)
        self._load_main_page_cookies()

    def get_oi(self, symbol: str, index: bool):
        if self.log_info:
            self.logger.info('Requesting Index OI')
        params = {'symbol': symbol.upper()}
        try:
            if index:
                return self._get(c.URL_INDICES, params)
            else:
                return self._get(c.URL_EQUITIES, params)
        except KeyError as e:
            self.logger.exception('Symbol: {} has error: {}'.format(symbol, e))

    def get_stocks_list(self, indices_symbol: str):
        """ Return combine list of stocks for indices stocks
        :param indices_symbol: (str): name of index like NIFTY 50, NIFTY BANK
        :return: dict
        """
        if self.log_info:
            self.logger.info('Requesting stock list of Index')

        indices_symbol = c.INDICES_TO_NAME[indices_symbol.upper()]
        params = {'index': indices_symbol}
        res = self._get(c.URL_STOCK_LIST, params=params)
        return res

    def _load_main_page(self):
        if self.log_info:
            self.logger.info('Requesting main page')
        res = self.session.get(c.URL_MAIN)
        if validate_res(res):
            with open('main_page_cookies.pickle', 'wb') as f:
                pickle.dump(self.session.cookies, f)
        if self.log_info:
            self.logger.info('Main Page loaded')

    def _get(self, url, params=None):
        """ Return response in dictionary format

        :param url: (str) url
        :param params: (dict) parameters of url
        :return: (dict) json
        """
        if self.log_info:
            self.logger.info('Sending Request: {}'.format(url))

        retry_counter = 0
        while retry_counter < 3:
            try:
                res = self.session.get(url, params=params)
                res_data = res.json()
                if validate_res(res) and res_data is not None:
                    if self.log_info:
                        self.logger.info('Response Received: {}'.format(url))
                    return res_data
                else:
                    self.logger.error('Not Validate Response: {} : {}'.format(str(params), url))
                    t.sleep(1)
                    self._load_main_page()
            except:
                t.sleep(1)
                self._load_main_page()
                self.logger.exception('Error with url: {}'.format(url), exc_info=True)
            retry_counter += 1

    def _load_main_page_cookies(self):
        try:
            with open('main_page_cookies.pickle', 'rb') as f:
                self.session.cookies = pickle.load(f)
        except FileNotFoundError:
            self._load_main_page()
