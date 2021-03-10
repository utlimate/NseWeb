import os
import json
import pickle
import requests
import urllib3
import nseapi.constant as c
from nseapi.logger import get_logger
from nseapi.data_models import IndexStocks, OpenInterest
import time as t
import socket
from nseapi.generic import validate_directory


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

    def __init__(self, log_info=None, logger=None, save_path=None):
        self._internet_connectivity = False

        self.logger = logger
        if self.logger is None:
            self.logger = get_logger('NseApi')

        if save_path is not None:
            c.HOME_DIR_PATH = save_path

        self.symbols_details = IndexStocks()
        self.log_info = log_info
        self.session = requests.Session()
        self.session.headers.update(c.HEADER)
        self._load_main_page()

    def get_oi(self, symbol: str, index: bool):
        if self.log_info:
            self.logger.info('Requesting Index OI')
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
                return OpenInterest(res)
        except KeyError as e:
            self.logger.exception('Symbol: {} has error: {}'.format(symbol, e))

    def get_stocks_list(self, indices_symbols: list):
        """ Return combine list of stocks for indices stocks
        :param indices_symbols: (str): name of index like NIFTY, BANKNIFTY
        :return: IndexStocks
        """
        if self.log_info:
            self.logger.info('Requesting stock list of Index')

        for i in indices_symbols:
            i = c.INDICES_TO_NAME[i.upper()]
            params = {'index': i}
            res = self._get(c.URL_STOCK_LIST, params=params, request_name='Stock List')
            self.symbols_details.add_data(res)
        return self.symbols_details

    def _load_main_page(self):
        if self.log_info:
            self.logger.info('Requesting main page')
        # res = self.session.get(c.URL_MAIN)
        res = self._get(c.URL_MAIN, request_name="Main Page", timeout=self.TIMEOUT)
        if res is not None:
            if validate_res(res):
                dir_path = c.HOME_DIR_PATH.joinpath('bin')
                validate_directory(dir_path)
                file_path = dir_path.joinpath('main_page_cookies.pickle')
                with open(file_path, 'wb') as f:
                    pickle.dump(self.session.cookies, f)
                if self.log_info:
                    self.logger.info('Main Page loaded')
            else:
                if self.log_info:
                    self.logger.info('Main Page loading Failed - Not valid response')
        else:
            self.logger.info('Main Page loading failed - response if none')

    def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        """ Return response in dictionary format

        :param url: (str) url
        :param params: (dict) parameters of url
        :return: (dict) json
        """
        retry_counter = 1
        while retry_counter <= self.MAX_RETRY:

            if self.log_info:
                self.logger.info('Sending Request - Try: {}, {}: {}'.format(retry_counter, request_name, str(params)))
            try:
                retry_counter += 1
                res = self.session.get(url, params=params, timeout=timeout)
                if validate_res(res):
                    try:
                        if request_name == 'Main Page':
                            res_data = res
                        else:
                            res_data = res.json()
                    except json.decoder.JSONDecodeError as e:
                        self.logger.exception('{}: {}'.format(request_name, str(params)), exc_info=True)
                        continue
                    if self.log_info:
                        self.logger.info('Response Received - {}: {}'.format(request_name, str(params)))
                    return res_data
                else:
                    self.logger.error('Not Validate Response - {}: {}'.format(request_name, str(params)))
                    t.sleep(self.RETRY_INTERVAL)
                    self._load_main_page()

            except (urllib3.exceptions.ReadTimeoutError, requests.exceptions.ConnectionError,
                    urllib3.exceptions.MaxRetryError, socket.gaierror, urllib3.exceptions.NewConnectionError) as rc:
                return None
                break
            except Exception as e:
                t.sleep(self.RETRY_INTERVAL)
                self._load_main_page()
                self.logger.exception('{}: {}'.format(request_name, str(params)), exc_info=True)

    def _load_main_page_cookies(self):
        try:
            if self.log_info:
                self.logger.info('loading cached cookies')
            file_path = c.HOME_DIR_PATH.joinpath('bin', 'main_page_cookies.pickle')
            with open(file_path, 'rb') as f:
                self.session.cookies = pickle.load(f)
        except FileNotFoundError:
            self._load_main_page()
