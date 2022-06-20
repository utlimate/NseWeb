import aiohttp
import asyncio


HEADER_NSE = {
    'accept-language': 'en-GB;q=0.5',
    'cache-control': 'no-cache',
    'sec-fetch-dest': 'document',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
}


URL_NSE = 'https://www.nseindia.com'
URL_GOOGLE = 'https://www.google.co.in'
URL_OC = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

async def main():
    async with aiohttp.ClientSession(headers=HEADER_NSE) as session:
        # Load Home Page
        async with session.get(URL_NSE) as resp:
            pass

        async with session.get(URL_OC) as resp:
            oi = await resp.json()
            print(oi)
            pass


loop = asyncio.get_event_loop()
loop.run_until_complete(main())