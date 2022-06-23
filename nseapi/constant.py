HOME_DIR_PATH = None
TODAY_DATE = None


URL_MAIN = "https://www.nseindia.com"
URL_INDICES = "https://www.nseindia.com/api/option-chain-indices"
URL_EQUITIES = "https://www.nseindia.com/api/option-chain-equities"
URL_MAIN = "https://www.nseindia.com"
URL_STOCK_LIST = "https://www.nseindia.com/api/equity-stockIndices"
URL_BANKNIFTY_STOCKS = "https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/bankNiftyStockWatch.json"

PATH_OI_INDICES = "api/option-chain-indices"
PATH_OI_EQUITIES = "api/option-chain-equities"
PATH_TURNOVER = "api/market-turnover"

HEADER_NSE = {
    'accept-language': 'en-GB;q=0.5',
    'cache-control': 'no-cache',
    'sec-fetch-dest': 'document',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
}

INDICES_TO_NAME = {
    'NIFTY': 'NIFTY 50',
    'BANKNIFTY': 'NIFTY BANK'
}

NAME_TO_INDICES = {
    'NIFTY 50': 'NIFTY',
    'NIFTY BANK': 'BANKNIFTY'
}

BASECOLUMNS = ['Strike Price', 'Expiry Date', 'Underlying Value']
RENAME_COLUMNS = {
    'strikePrice': 'Strike Price',
    'expiryDate': 'Expiry Date',
    'underlying': 'Underlying',
    'identifier': 'Identifier',
    'openInterest': 'Open Interest',
    'changeinOpenInterest': 'Change in Open Interest',
    'pchangeinOpenInterest': 'P.Change in Open Interest',
    'totalTradedVolume': 'Total Traded Volume',
    'impliedVolatility': 'Implied Volatility',
    'lastPrice': 'Last Price',
    'change': 'Change',
    'pChange': 'P.Change',
    'totalBuyQuantity': 'Total Buy Quantity',
    'totalSellQuantity': 'Total Sell Quantity',
    'bidQty': 'Bid Qty',
    'bidprice': 'Bid Price',
    'askQty': 'Ask Qty',
    'askPrice': 'Ask Price',
    'underlyingValue': 'Underlying Value'
}
