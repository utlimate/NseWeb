from nseapi import NseApi
from nseapi.data_models import ExpiryDates
import pandas as pd

from nseapi.data_models import OpenInterest

nse = NseApi(log_info=True)
# nse.get_stocks_list(['Nifty', 'Banknifty'])
oi = nse.get_oi('nifty', index=True)
# oiobj = OpenInterest(oi)
# ed = ExpiryDates(oi.df['Expiry Date'])
# ed_weekly = ed.near_expiry.weekly_expiry
# near = oi.near_expriry
near_next = oi.get_by_expiry(['25-02-21', '04-03-21'])
next_current = oi.trim()
print('Test')