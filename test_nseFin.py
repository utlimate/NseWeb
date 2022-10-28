import unittest
from nseapi.financial.requester import BaseFinApiAsync, FinApiAsync


class TestAsyncBaseNseFinApi(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.nse = BaseFinApiAsync()
        self.nse.main()

    async def test_results(self):
        result = await self.nse.results('equities', 'Reliance')
        self.assertIsNotNone(result, 'result is None')
        self.assertTrue(result.ok, f"Response is not valid, Status Code:{result.status}")
        result = await result.json()
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, list, msg=f'Data is not list, but it is {type(result)}.')
        self.assertNotEqual(len(result), 0, msg='Data is empty')


class TestAsyncNseFinApi(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.nse = FinApiAsync()
        self.nse.main()

    async def test_results(self):
        result = await self.nse.results('equities', 'reliance')
        self.assertIsNotNone(result, 'result is None')
        self.assertIsInstance(result, list, f"result is not list, type: {type(result)}")
        self.assertGreater(len(result), 0, f"result is empty, length: {len(result)}")


if __name__ == '__main__':
    unittest.main()

