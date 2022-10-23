import unittest
from nseapi import NseApiAsync

class TestAsyncNseApi(unittest.TestCase):
    TIMEOUT = 5

    async def asyncSetUp(self):
        self.nse = NseApiAsync()

    async def test_marketTurnover(self):
        fut = await self.nse.market_turnover()
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIsInstance(result['data'], list, msg=f'Data is not list, but it is {type(result["data"])}.')
        self.assertNotEqual(len(result['data']), 0, msg='Data is empty')

    async def test_optionChain(self):
        fut = await self.nse.option_chain("NIFTY", True)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('records', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['records']), 0, msg='Data is empty')

    async def test_search(self):
        fut = await self.nse.search('reliance')
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('symbols', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['symbols']), 0, msg='Data is empty')

    async def test_quote(self):
        fut = await self.nse.quote('RELIANCE', section=NseApiAsync.SECTION_TRADEINFO)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('info', result.keys(), msg=f"info is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['info']), 0, msg='Data is empty')

        fut = await self.nse.quote('RELIANCE', section=NseApiAsync.SECTION_CORPINFO)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('corporate', result.keys(), msg=f"corporate is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['corporate']), 0, msg='Data is empty')

    async def test_corpInfo(self):
        fut = await self.nse.corp_info('RELIANCE')
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('corporate', result.keys(), msg=f"corporate is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['corporate']), 0, msg='Data is empty')

    async def test_chartData(self):
        fut = await self.nse.chartdata_index('NIFTY 50', index=True)
        result = fut.result(self.TIMEOUT)
        print(result)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('name', result.keys(), msg=f"name is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['grapthData']), 0, msg='Data is empty')

        fut = await self.nse.chartdata_index('RELIANCE', index=False)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('name', result.keys(), msg=f"name is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['grapthData']), 0, msg='Data is empty')

        fut = await self.nse.chartdata_index('RELIANCE', index=False, preopen=True,)
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('name', result.keys(), msg=f"name is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['grapthData']), 0, msg='Data is empty')

    async def test_marketState(self):
        fut = await self.nse.market_status()
        result = fut.result(self.TIMEOUT)
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('marketState', result.keys(), msg=f"marketState is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['marketState']), 0, msg='Data is empty')


if __name__ == '__main__':
    unittest.main()


# class TestNseApi(unittest.TestCase):
#     TIMEOUT = 5
#     nse = NseApiAsync()
#     loop = asyncio.get_event_loop()
#     futs = []
#     loop_thread = threading.Thread(target = loop.run_forever, daemon=True)
#     loop_thread.start()

#     def test_marketTurnover(self):
#         fut = asyncio.run_coroutine_threadsafe(self.nse.market_turnover(), loop=self.loop)
#         result = fut.result(self.TIMEOUT)
#         self.assertIsNotNone(result, 'result is None')
#         self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
#         self.assertIsInstance(result['data'], list, msg=f'Data is not list, but it is {type(result["data"])}.')
#         self.assertNotEqual(len(result['data']), 0, msg='Data is empty')

#     def test_optionChain(self):
#         fut = asyncio.run_coroutine_threadsafe(self.nse.option_chain("NIFTY", True), loop=self.loop)
#         result = fut.result(self.TIMEOUT)
#         self.assertIsNotNone(result, 'result is None')
#         self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
#         self.assertIn('records', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
#         self.assertNotEqual(len(result['records']), 0, msg='Data is empty')

#     def test_Search(self):
#         fut = asyncio.run_coroutine_threadsafe(self.nse.search('reliance'), loop=self.loop)
#         result = fut.result(self.TIMEOUT)
#         self.assertIsNotNone(result, 'result is None')
#         self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
#         self.assertIn('symbols', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
#         self.assertNotEqual(len(result['symbols']), 0, msg='Data is empty')

#     def test_getQuote(self):
#         fut = asyncio.run_coroutine_threadsafe(self.nse.get_quote('RELIANCE'), loop=self.loop)
#         result = fut.result(self.TIMEOUT)
#         self.assertIsNotNone(result, 'result is None')
#         self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
#         self.assertIn('info', result.keys(), msg=f"info is not available in results. Keys are {list(result.keys())}")
#         self.assertNotEqual(len(result['info']), 0, msg='Data is empty')

#     def test_corpInfo(self):
#         fut = asyncio.run_coroutine_threadsafe(self.nse.corp_info('RELIANCE'), loop=self.loop)
#         result = fut.result(self.TIMEOUT)
#         self.assertIsNotNone(result, 'result is None')
#         self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
#         self.assertIn('corporate', result.keys(), msg=f"corporate is not available in results. Keys are {list(result.keys())}")
#         self.assertNotEqual(len(result['corporate']), 0, msg='Data is empty')
