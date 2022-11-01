import unittest
from scrapper.nseapi.requester import BaseNseApiAsync


class TestAsyncBaseNseApi(unittest.IsolatedAsyncioTestCase):
    TIMEOUT = 5

    async def asyncSetUp(self):
        self.nse = BaseNseApiAsync()
        self.nse.main()

    async def test_marketTurnover(self):
        result = await self.nse.market_turnover()
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result['data'], list, msg=f'Data is not list, but it is {type(result["data"])}.')
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIsNotNone(result, 'result is None')
        self.assertNotEqual(len(result['data']), 0, msg='Data is empty')

    async def test_optionChain(self):
        result = await self.nse.option_chain("NIFTY", True)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('records', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['records']), 0, msg='Data is empty')

    async def test_search(self):
        result = await self.nse.search('reliance')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('symbols', result.keys(), msg=f"records is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['symbols']), 0, msg='Data is empty')

    async def test_quote(self):
        result = await self.nse.quote('RELIANCE', section=BaseNseApiAsync.SECTION_TRADEINFO)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertNotEqual(len(result), 0, msg='Data is empty')

        result = await self.nse.quote('RELIANCE', section=BaseNseApiAsync.SECTION_CORPINFO)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('corporate', result.keys(), msg=f"corporate is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['corporate']), 0, msg='Data is empty')

    async def test_corpInfo(self):
        result = await self.nse.corp_info('RELIANCE')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('corporate', result.keys(), msg=f"corporate is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['corporate']), 0, msg='Data is empty')

    async def test_chartDataIndex(self):
        # For Index
        result = await self.nse.chart_data('NIFTY 50', index=True)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        try:
            result = await result.json()
        except:
            result = await result.text()
            self.fail(str(result))
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('grapthData', result.keys(), msg=f"grapthData is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['grapthData']), 0, msg='Data is empty')
    
    async def test_chartDataStock(self):
        # For Stock
        result = await self.nse.chart_data('RELIANCE', False)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        try:
            result = await result.json()
        except:
            result = await result.text()
            self.fail(str(result))
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        # This can be empty
        self.assertIn('grapthData', result.keys(), msg=f"grapthData is not available in results. Keys are {list(result.keys())}")
        # self.assertNotEqual(len(result['grapthData']), 0, msg='Data is empty')

    async def test_chartDataPreopen(self):
        # Stock with PreOpen
        result = await self.nse.chart_data('RELIANCE', index=False, preopen=True,)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        try:
            result = await result.json()
        except:
            result = await result.text()
            self.fail(str(result))
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        # This can be empty
        self.assertIn('grapthData', result.keys(), msg=f"grapthData is not available in results. Keys are {list(result.keys())}")
        # self.assertNotEqual(len(result['grapthData']), 0, msg='Data is empty')

    async def test_marketStatus(self):
        result = await self.nse.market_status()
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('marketState', result.keys(), msg=f"marketState is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result['marketState']), 0, msg='Data is empty')

    async def test_master(self):
        result = await self.nse.master()
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, list, msg=f"response is not list, but it is {type(result)}.")
        self.assertNotEqual(len(result), 0, msg='Data is empty')

    async def test_dailyReport(self):
        # Cash
        result = await self.nse.daily_report(BaseNseApiAsync.SEGMENT_CASH)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, list, msg=f"response is not list, but it is {type(result)}.")
        self.assertNotEqual(len(result), 0, msg='Data is empty')

        # Derivative
        result = await self.nse.daily_report(BaseNseApiAsync.SEGMENT_DERIVATIVE)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, list, msg=f"response is not list, but it is {type(result)}.")
        self.assertNotEqual(len(result), 0, msg='Data is empty')

        # Debt
        result = await self.nse.daily_report(BaseNseApiAsync.SEGMENT_DEBT)
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, list, msg=f"response is not list, but it is {type(result)}.")
        self.assertNotEqual(len(result), 0, msg='Data is empty')

    async def test_metaInfo(self):
        result = await self.nse.meta_info('RELIANCE')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('symbol', result.keys(), msg=f"marketState is not available in results. Keys are {list(result.keys())}")
        self.assertNotEqual(len(result), 0, msg='Data is empty')

    async def test_historyDerivativ(self):
        result = await self.nse.history_deri('NIFTY 50')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('data', result.keys(), msg=f"data is not available in results. Keys are {list(result.keys())}")

    async def test_historyEquity(self):
        result = await self.nse.history_equity('RELIANCE')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('data', result.keys(), msg=f"data is not available in results. Keys are {list(result.keys())}")

        result = await self.nse.history_equity('RELIANCE', from_date='24-09-2022', to_date='24-10-2022')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('data', result.keys(), msg=f"data is not available in results. Keys are {list(result.keys())}")

    async def test_bulkblock(self):
        result = await self.nse.bulkandblock('RELIANCE')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('data', result.keys(), msg=f"data is not available in results. Keys are {list(result.keys())}")

        result = await self.nse.bulkandblock('RELIANCE', from_date='24-09-2022', to_date='24-10-2022')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('data', result.keys(), msg=f"data is not available in results. Keys are {list(result.keys())}")

    async def test_highLow(self):
        result = await self.nse.high_low('RELIANCE')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('_id', result.keys(), msg=f"data is not available in results. Keys are {list(result.keys())}")

        result = await self.nse.high_low('RELIANCE', year='2022')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
        self.assertIn('_id', result.keys(), msg=f"data is not available in results. Keys are {list(result.keys())}")


if __name__ == '__main__':
    unittest.main()


# fut = await self.nse.market_turnover()
# result = fut.result(self.TIMEOUT)
# self.assertEqual(result.status, 200, f"Status code is not valid {result.status}")
# self.assertIsNotNone(result, 'result is None')
# self.assertIsInstance(result, dict, msg=f"response is not dictonary, but it is {type(result)}.")
# self.assertIsInstance(result['data'], list, msg=f'Data is not list, but it is {type(result["data"])}.')
# self.assertNotEqual(len(result['data']), 0, msg='Data is empty')

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
