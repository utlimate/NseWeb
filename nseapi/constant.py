URL_INDICES = "https://www.nseindia.com/api/option-chain-indices"
URL_EQUITIES = "https://www.nseindia.com/api/option-chain-equities"
URL_MAIN = "https://www.nseindia.com"
URL_STOCK_LIST = "https://www.nseindia.com/api/equity-stockIndices"
URL_BANKNIFTY_STOCKS = "https://www1.nseindia.com/live_market/dynaContent/live_watch/stock_watch/bankNiftyStockWatch.json"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Safari/537.36/8mqPaQuL-91"
}

INDICES_TO_NAME = {
    'NIFTY': 'NIFTY 50',
    'BANKNIFTY': 'NIFTY BANK'
}

NAME_TO_INDICES = {
    'NIFTY 50': 'NIFTY',
    'NIFTY BANK': 'BANKNIFTY'
}
