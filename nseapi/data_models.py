from datetime import datetime
from typing import Union
import pandas as pd
import numpy as np
import nseapi.constant as c
pd.options.mode.chained_assignment = None  # default='warn'


def rename_columns_old(columns):
    """ Return dictonary with old_name: new_name """

    def first_letter_upper(name):
        name_list = list(name)
        name_list[0] = name_list[0].upper()
        return ''.join(name_list)

    columns_new = {}
    for c in columns:
        c_name = list(c.split('_'))
        c_name = [first_letter_upper(l) for l in c_name]
        if len(c_name) > 1:
            columns_new[c] = c_name[-1] + ' ' + ''.join(c_name[:-1])
        else:
            columns_new[c] = c_name[0]
    return columns_new


def rename_columns(df):
    """ Return dictonary with old_name: new_name """
    # columns = {k: v for k, v in c.RENAME_COLUMNS.items() if k in df.columns}
    
    columns = {}

    for column in df.columns:
        column_parts = column.split(' ')
        new_column = column
        # Change position of Call or Put to First
        if column_parts[-1] in ['Call', 'Put']:
            new_column_parts = [column_parts[-1]]
            new_column_parts.extend(column_parts[:-1])
            new_column = ' '.join(new_column_parts)

        # Change as per constant RENAME COLUMNS
        if new_column in c.RENAME_COLUMNS.keys():
            new_column = c.RENAME_COLUMNS[new_column]

        columns[column] = new_column

    df.rename(columns=columns, inplace=True)


def normalize_oi_data(raw_data: dict):
    records_ce = []
    records_pe = []
    filtered_ce = []
    filtered_pe = []

    # parsing records data
    for d in raw_data['records']['data']:

        try:
            records_ce.append(d['CE'])
        except KeyError:
            pass

        try:
            records_pe.append(d['PE'])
        except KeyError:
            pass
    raw_data['records']['data'] = {
        'CE': records_ce,
        'PE': records_pe
    }

    # parsing filtered_data
    for d in raw_data['filtered']['data']:
        try:
            filtered_ce.append(d['CE'])
        except KeyError:
            pass

        try:
            filtered_pe.append(d['PE'])
        except KeyError:
            pass

    raw_data['filtered']['data'] = {
        'CE': filtered_ce,
        'PE': filtered_pe
    }
    return raw_data


def data_to_dataframe(data: dict):
    call_df = pd.DataFrame(data['CE'])
    call_df.drop(['bidQty', 'bidprice', 'askQty', 'askPrice'], axis=1, inplace=True)
    rename_columns(call_df)

    put_df = pd.DataFrame(data['PE'])
    put_df.drop(['underlying', 'bidQty', 'bidprice', 'askQty', 'askPrice'], axis=1, inplace=True)
    rename_columns(put_df)

    df = pd.merge(call_df, put_df, on=c.BASECOLUMNS, suffixes=[' Call', ' Put'])
    df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], dayfirst=True)
    # df['Expiry Date'] = df['Expiry Date'].apply(lambda x: x.strftime('%d-%m-%y'))
    rename_columns(df)
    return df

class OptionChain:
    """ Hold Option Chain Data for symbol """

    def __init__(self, data):
        self.time_stamp = None
        self.expiry_dates = None
        if isinstance(data, OptionChain):
            self.df = data.df
            self.time_stamp = data.time_stamp
        else:
            self._prepare_data(data)

    def _prepare_data(self, data):
        if data is None:
            raise ValueError('data is None')
        if isinstance(data, pd.DataFrame):
            self.df = pd.DataFrame(data)
        else:
            data = normalize_oi_data(data)
            try:
                self.time_stamp = data['records']['timestamp']
            except KeyError:
                print('timestamp not in keys')
            self.df = data_to_dataframe(data['records']['data'])
        self.expiry_dates = ExpiryDates(self.df['Expiry Date'])

        if isinstance(self.time_stamp, str):
            self.time_stamp = datetime.strptime(self.time_stamp, '%d-%b-%Y %H:%M:%S')

    @property
    def middle_strike(self) -> Union[np.int64, np.float64, np.float32, np.int, np.float]:
        df = self.df.iloc[(self.df['Strike Price'] - self.underlying_value).abs().argsort()[:1]]
        df = df['Strike Price']
        if len(df.unique()) > 1:
            raise ValueError('More then one strike found')
        else:
            return df.values[0]

    @property
    def strike_prices(self) -> list:
        """ Return list of sorted Stike Prices

        Returns:
            list: Sorted list of strike prices
        """        
        return sorted(list(self.df['Strike Price'].unique()))

    @property
    def underlying_value(self) -> Union[float, int]:
        """ Return underlying value of the symbol

        Raises:
            ValueError: if there is more than one symbol

        Returns:
            [float or int]:
        """
        ticker = list(set(self.df['Underlying Value']))
        if len(ticker) > 1:
            raise ValueError("More than one symbol found")
        return ticker[0]

    @property
    def time_string(self) -> str:
        """ Return time in 24h string"""
        return self.time_stamp.time().strftime('%H:%M:%S')

    @property
    def date_string(self) -> str:
        """ Return date in string """
        return self.time_stamp.date().strftime('%d-%b-%Y')

    @property
    def symbol(self) -> str:
        """ Return underlying symbol

        Raises:
            ValueError: If there is more than one symbol in option chain

        Returns:
            [str]: like nifty, reliance
        """
        ticker = list(set(self.df['Underlying']))
        if len(ticker) > 1:
            raise ValueError("More than one symbol found")
        return ticker[0]

    @property
    def near_expriry(self) -> 'OptionChain':
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.near_expiry.values)]
        df = self.__class__(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def next_expiry(self) -> 'OptionChain':
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.next_expiry.values)]
        df = self.__class__(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def far_expiry(self) -> 'OptionChain':
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.far_expiry.values)]
        df = self.__class__(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def monthly_expiry(self) -> 'OptionChain':
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.monthly_expiry.values)]
        df = self.__class__(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def weekly_expiry(self) -> 'OptionChain':
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.weekly_expiry.values)]
        df = self.__class__(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def current_expiry(self) -> 'OptionChain':
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.current_expiry.values)]
        df = self.__class__(df)
        df.time_stamp = self.time_stamp
        return df

    def get_by_strike(self, price, condition: str = 'equal'):
        """ Get data above or below or equal to price
        :param price: (float, int): price from which to perform action
        :param condition: (str): which condition to perform. (above, below or equal are valid)
        """
        df = None
        if condition.lower() == 'equal':
            df = OptionChain(self.df[self.df['Strike Price'] == price])
        elif condition.lower() == 'above':
            df = OptionChain(self.df[self.df['Strike Price'] > price])
        elif condition.lower() == 'below':
            df = OptionChain(self.df[self.df['Strike Price'] < price])
        df.time_stamp = self.time_stamp
        return df

    def get_by_expiry(self, expiry_date: Union[datetime, str, list]):
        """ To get only data of selected expiry date

        :param expiry_date: (datetime, str, list) get all data of data
        :return OpenInterest
        """
        df = None
        if isinstance(expiry_date, str):
            expiry_date = datetime.strptime(expiry_date, '%d-%m-%y')
            df = self.df[self.df['Expiry Date'] == expiry_date]
        elif isinstance(expiry_date, list):
            expiry_date = [datetime.strptime(e, '%d-%m-%y') for e in expiry_date if isinstance(e, str)]
            df = self.df.loc[self.df['Expiry Date'].isin(expiry_date)]
        else:
            if not isinstance(expiry_date, datetime) and not isinstance(expiry_date, list):
                raise TypeError('expiry_date must be datetime')

        if len(df) < 1:
            raise ValueError('Expiry Date not found')

        df = OptionChain(df)
        df.time_stamp = self.time_stamp
        return df

    def trim(self, strikes: int = 5):
        """ Will trim data to above and below till strikes from underling value and also inclue middle_strike
        :param strikes: int: default 5
        :return OpenInerest
        """
        # Get All Strike Price above middle strike price
        strikes_prices = pd.Series(self.strike_prices)
        above_strikes = strikes_prices.loc[strikes_prices > self.middle_strike]
        above_strikes.sort_values(inplace=True)
        above_strikes = above_strikes.iloc[:strikes]

        # Get all strike price below middle strike price
        below_strikes = strikes_prices.loc[strikes_prices < self.middle_strike]
        below_strikes.sort_values(inplace=True, ascending=False)
        below_strikes = below_strikes.iloc[:strikes]


        strikes_prices = pd.concat([above_strikes, below_strikes], ignore_index=True)
        # Add middle strike price to series
        strikes_prices = strikes_prices.append(pd.Series([self.middle_strike]), ignore_index=True, verify_integrity=True)
        strikes_prices.sort_values(inplace=True)
        strikes_prices.reset_index(drop=True, inplace=True)

        df = self.df.loc[self.df['Strike Price'].isin(strikes_prices.values)]
        # df = self.df.iloc[(self.df['Strike Price'] - self.underlying_value).abs().argsort()[:strikes * 2]]
        df = OptionChain(df)
        df.time_stamp = self.time_stamp
        return df

    def to_dict(self):
        return self.df.to_dict(orient='records')

    def __str__(self):
        return self.df.__str__()

    def __repr__(self):
        return self.df.__repr__()

    def __iter__(self):
        return self.df.__iter__()

    def __getitem__(self, item):
        return self.df.__getitem__(item)

    def __setitem__(self, key, value):
        self.df.__setitem__(key, value)

    def __len__(self):
        return self.df.__len__()

    def __call__(self, *args, **kwargs):
        return self.df

    # def __getattr__(self, item):
    #     return self.df.__getattr__(item)


class IndexStocks:
    """ Hold all symbols details for indices """

    def __init__(self):
        self.data = pd.DataFrame()

    def get_prev_close(self, symbol):
        data = self.data[self.data['symbol'] == symbol]['previousClose']
        if data.empty:
            raise KeyError('{} not in symbols'.format(data))
        else:
            return float(data.values[0])

    def get_stocks(self) -> list:
        """ Get sorted stock list of indices

        :return: list
        """
        df = self.data.loc[self.data['priority'] == 0]
        df.sort_values(['identifier'], ascending=bool, inplace=True)
        return list(df['symbol'])

    def get_indices(self) -> list:
        """ Get sorted indices list of indices

        :return: list
        """
        df = self.data.loc[self.data['priority'] == 1]
        df.sort_values(['identifier'], ascending=bool, inplace=True)
        return list(df['symbol'])

    def get_list(self) -> list:
        """ get both indices and stocks symbols

        :return: sorted list
        """
        indices = self.get_indices()
        indices.extend(self.get_stocks())
        return indices

    @staticmethod
    def prepare_data(data):
        df = pd.DataFrame(data)
        return df

    def add_data(self, data):
        """ Add to Index Details
        append data to existing data
        rename index name to index symbol
        drop duplicate

        :param data: (dict)
        :return: self
        """
        if self.data.empty:
            self.data = pd.DataFrame(data['data'])
        else:
            # Append Data to symbols
            df = self.prepare_data(data['data'])
            self.data = self.data.append(df, ignore_index=True)

        # Replace index symbol
        index_name = data['metadata']['indexName']

        # Drop meta column. Meta column has dict. Which cause TypeError in drop_duplicates
        self.data.drop(['meta'], axis=1, inplace=True)
        self.data.drop_duplicates(inplace=True)

        self.data.symbol[self.data.symbol == index_name] = c.NAME_TO_INDICES[index_name]
        self.data.sort_values(['identifier'], ascending=bool)
        return self

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()

    def __iter__(self):
        return self.data.__iter__()

    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def __setitem__(self, key, value):
        self.data.__setitem__(key, value)

    def __len__(self):
        return self.data.__len__()


class ExpiryDates:
    def __init__(self, data):
        if isinstance(data, pd.Series):
            data = data.copy()
        else:
            try:
                _ = iter(data)
                data = pd.Series(data)
            except TypeError:
                raise TypeError('data must be pandas.Series or Iterables')

        self.data = data
        self.data.drop_duplicates(keep='first', inplace=True)
        self.data.sort_values(inplace=True)
        self.datetime_index = pd.DatetimeIndex(data)
        self.months = sorted(self.datetime_index.month.unique())

    @property
    def values(self):
        return self.data.values

    @property
    def current_expiry(self):
        return ExpiryDates([self.data.min()])

    @property
    def near_expiry(self):
        near_month = min(self.months)
        near_series = self.data.loc[self.datetime_index.month == near_month]
        return ExpiryDates(near_series)

    @property
    def next_expiry(self):
        near_month = min(self.months) + 1
        near_series = self.data.loc[self.datetime_index.month == near_month]
        return ExpiryDates(near_series)

    @property
    def far_expiry(self):
        near_month = min(self.months) + 1
        near_series = self.data.loc[self.datetime_index.month > near_month]
        return ExpiryDates(near_series)

    @property
    def monthly_expiry(self):
        results = []
        for i, m in enumerate(self.months):
            m_data = self.data.loc[self.datetime_index.month == m]
            results.append(m_data.max())
        results = pd.Series(results)
        results.drop_duplicates(keep='first', inplace=True)
        results.sort_values(inplace=True)
        return ExpiryDates(results)

    @property
    def weekly_expiry(self):
        near = self.near_expiry.data
        if len(near) > 1:
            near = near.iloc[:-1]

        return ExpiryDates(near)
