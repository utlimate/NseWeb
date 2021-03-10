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
    REQUEST_EXCEPTION = (requests.exceptions.Timeout,
                         requests.exceptions.ConnectionError,
                         requests.exceptions.HTTPError,
                         urllib3.exceptions.ReadTimeoutError,
                         urllib3.exceptions.MaxRetryError,
                         socket.gaierror,
                         urllib3.exceptions.NewConnectionError
                         )

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
        self.main_page_loaded = False
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

    def _load_main_page(self):
        try:
            if self.log_info:
                self.logger.info('Requesting main page')
            res = self.session.get(c.URL_MAIN, timeout=self.TIMEOUT)
            if validate_res(res):
                self.main_page_loaded = True
                dir_path = c.HOME_DIR_PATH.joinpath('bin')
                validate_directory(dir_path)
                file_path = dir_path.joinpath('main_page_cookies.pickle')
                with open(file_path, 'wb') as f:
                    pickle.dump(self.session.cookies, f)
                if self.log_info:
                    self.logger.info('Main Page loaded')
            else:
                if self.log_info:
                    self.logger.error(f'Main Page loading Failed - Not valid response, Status Code: {res.status_code}')
        except self.REQUEST_EXCEPTION as e:
            self.logger.error(f'Network error in load Main Page')
        except Exception:
            self.logger.exception('Load Main page has an error', exc_info=True)

    def _get(self, url, params=None, request_name=None, timeout=TIMEOUT):
        res_data = None
        for i in range(1, self.MAX_RETRY + 1):
            if self.log_info:
                self.logger.info(f'Sending Request - Try: {i}, {request_name}: {str(params)}')

            try:
                if self.main_page_loaded:
                    res = self.session.get(url, params=params, timeout=timeout)
                    if validate_res(res):
                        res_data = res.json()

                        if self.log_info:
                            self.logger.info(f'Response Received - {request_name}: {str(params)}')
                        break   # breaking loop on successfull response
                    else:
                        self.logger.error(f'{request_name}: Not Validate Response, Status Code: {res.status_code}')
                        t.sleep(self.RETRY_INTERVAL)
                        self.main_page_loaded = False
                        self._load_main_page()
                else:
                    self.logger.error('Main Page still not loaded. Load Main Page First')
                    self._load_main_page()

            except self.REQUEST_EXCEPTION as rc:
                self.logger.error(f'{request_name}: has network error')
                break
            except json.decoder.JSONDecodeError as e:
                self.logger.exception(f'{request_name}: Not Valid Json Data')
            except Exception as e:
                self.main_page_loaded = False
                t.sleep(self.RETRY_INTERVAL)
                self._load_main_page()
                self.logger.exception(f'Name:{request_name}, Params: {params}', exc_info=True)

        return res_data

    def _load_main_page_cookies(self):
        try:
            if self.log_info:
                self.logger.info('loading cached cookies')
            file_path = c.HOME_DIR_PATH.joinpath('bin', 'main_page_cookies.pickle')
            with open(file_path, 'rb') as f:
                self.session.cookies = pickle.load(f)
        except FileNotFoundError:
            self._load_main_page()
