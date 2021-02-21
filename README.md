# NseWeb

This repository use to download option chain data from NSE website

<b>Usage:</b>
nse = NseWeb()

# To Download Index Symbol List:
stock_list = nse.get_stocks_list('NIFTY 50')

# To downlaod option chain data
  # For Index
  oi_data = nse.get_oi('NIFTY', index=True)
  
  # For Stock
  oi_data = nse.get_oi('INFY', index=False)
