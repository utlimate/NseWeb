HOME_DIR_PATH = None
TODAY_DATE = None


URL_MAIN = "https://www.nseindia.com"
URL_API = URL_MAIN + "/api"
URL_HISTORICAL = URL_API + "/historical"
URL_INDICES = "https://www.nseindia.com/api/option-chain-indices"
URL_EQUITIES = "https://www.nseindia.com/api/option-chain-equities"
URL_MAIN = "https://www.nseindia.com"
URL_STOCK_LIST = "https://www.nseindia.com/api/equity-stockIndices"
URL_BANKNIFTY_STOCKS = "https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/bankNiftyStockWatch.json"

PATH_OI_INDICES = "/option-chain-indices"
PATH_OI_EQUITIES = "/option-chain-equities"
PATH_TURNOVER = "/market-turnover"
PATH_SEARCH = "/search/autocomplete"
PATH_GET_QUOTE = "/quote-equity"
PATH_CHARTDATA_INDEX = "/chart-databyindex"
PATH_MARKETSTATUS = "/marketStatus"
PATH_META_INFO = "/equity-meta-info"
PATH_MASTER = "/master-quote"
PATH_DAILY_REPORT = "/merged-daily-reports"
PATH_QUOTE_DERIVATIVE = "/quote-derivative"
PATH_HISTORY = "/historical"
PATH_HISTORY_DERIVATIVES = PATH_HISTORY + "/fo/derivatives"
PATH_HISTORY_DERIVATIVES_META = PATH_HISTORY_DERIVATIVES + "/meta"
PATH_HIS_EQUITY = PATH_HISTORY + "/cm/equity"
PATH_BULKBLOCK = PATH_HISTORY + "/cm/bulkAndblock"
PATH_HIGHLOW = PATH_HISTORY + "/cm/high-low"

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
