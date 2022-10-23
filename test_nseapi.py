import unittest
import threading
from collections.abc import MutableMapping
from unittest import result
from nseapi import NseApiAsync
from nseapi.requester import Ticker
import asyncio


class TestNseApi(unittest.TestCase):
    TIMEOUT = 5
    nse = NseApiAsync()
    loop = asyncio.get_event_loop()
    futs = []
    loop_thread = threading.Thread(target = loop.run_forever, daemon=True)
    loop_thread.start()

    def test_marketTurnover(self):
        fut = asyncio.run_coroutine_threadsafe(self.nse.market_turnover(), loop=self.loop)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIsInstance(result['data'], list, msg=f'Data is not list, but it is {type(result["data"])}.')
        self.assertNotEqual(len(result['data']), 0, msg='Data is empty')

    def test_optionChain(self):
        fut = asyncio.run_coroutine_threadsafe(self.nse.option_chain("NIFTY", True), loop=self.loop)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('records', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['records']), 0, msg='Data is empty')

    def test_Search(self):
        fut = asyncio.run_coroutine_threadsafe(self.nse.search('reliance'), loop=self.loop)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('symbols', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['symbols']), 0, msg='Data is empty')

    def test_getQuote(self):
        fut = asyncio.run_coroutine_threadsafe(self.nse.get_quote('RELIANCE'), loop=self.loop)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('info', result.keys(), msg=f"info is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['info']), 0, msg='Data is empty')

    def test_corpInfo(self):
        fut = asyncio.run_coroutine_threadsafe(self.nse.corp_info('RELIANCE'), loop=self.loop)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('corporate', result.keys(), msg=f"corporate is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['corporate']), 0, msg='Data is empty')

if __name__ == '__main__':
    unittest.main()