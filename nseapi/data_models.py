from datetime import datetime
from typing import Union
import pandas as pd
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


class OIObj:
    """ Data object for nse res
        Parse data in parameters """

    def __init__(self, data, underlying_value=None, time_stamp=None):
        self.underlying_value = underlying_value
        self.time_stamp = time_stamp

        if isinstance(data, pd.DataFrame):
            self.df = pd.DataFrame(data)
        else:
            self._parse_dict(data)

        if isinstance(self.time_stamp, str):
            self.time_stamp = datetime.strptime(self.time_stamp, '%d-%b-%Y %H:%M:%S')

    def _parse_dict(self, data):
        data = normalize_oi_data(data)
        try:
            self.underlying_value = data['records']['underlyingValue']
        except KeyError:
            print('underlyingValue not in keys')

        try:
            self.time_stamp = data['records']['timestamp']
        except KeyError:
            print('timestamp not in keys')

        self.df = data_to_dataframe(data['records']['data'])
        self.filtered_df = data_to_dataframe(data['filtered']['data'])

    @property
    def time_string(self):
        """ Return time in 24h string"""
        return self.time_stamp.time().strftime('%H:%M:%S')

    @property
    def date_string(self):
        """ Return date in string """
        return self.time_stamp.date().strftime('%d-%b-%Y')

    @property
    def expiry_dates(self):
        """ Get expiry_dates from data
        :exception ValueError: if there is more than one expiry date in data
        return Expi
        """
        return list(set(self.df['Expiry Date'].values))

    @property
    def symbol(self):
        ticker = list(set(self.df['Underlying']))
        if len(ticker) > 1:
            raise ValueError("More than one symbol found")
        return ticker[0]

    def get_by_strike(self, price, condition: str = 'equal'):
        """ Get data above or below or equal to price
        :param price: (float, int): price from which to perform action
        :param condition: (str): which condition to perform. (above, below or equal are valid)
        """
        if condition.lower() == 'equal':
            return OIObj(self.df[self.df['Strike Price'] == price], self.underlying_value, self.time_stamp)
        elif condition.lower() == 'above':
            return OIObj(self.df[self.df['Strike Price'] > price], self.underlying_value, self.time_stamp)
        elif condition.lower() == 'below':
            return OIObj(self.df[self.df['Strike Price'] < price], self.underlying_value, self.time_stamp)

    def get_by_expiry(self, expiry_date: Union[datetime, str]):
        """ To get only data of selected expiry date

        :param expiry_date: (datetime) get all data of data
        :return OIObj
        """

        if isinstance(expiry_date, str):
            expiry_date = datetime.strptime(expiry_date, '%d-%m-%y')

        if not isinstance(expiry_date, datetime):
            raise TypeError('expiry_date must be datetime')
        else:
            expiry_date = expiry_date.strftime('%d-%m-%y')

        df = self.df[self.df['Expiry Date'] == expiry_date]

        if len(df) <= 0:
            expiry_date = min(pd.to_datetime(self.df['Expiry Date'], dayfirst=True)).date().strftime('%d-%m-%y')
            df = self.df[self.df['Expiry Date'] == expiry_date]

        return OIObj(df, self.underlying_value, self.time_stamp)

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


class OpenInterest:
    """ Data object for nse res
        Parse data in parameters """

    def __init__(self, data):
        self.time_stamp = None
        self.strike_interval = None
        self.expiry_dates = None

        self._prepare_data(data)

        if isinstance(self.time_stamp, str):
            self.time_stamp = datetime.strptime(self.time_stamp, '%d-%b-%Y %H:%M:%S')

    def _prepare_data(self, data):
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
        self.strike_interval = self.strike_prices[1] - self.strike_prices[0]

    @property
    def middle(self):
        df = self.df.iloc[(self.df['Strike Price'] - self.underlying_value).abs().argsort()[:1]]
        return df['Strike Price']

    @property
    def middle_strike(self):
        df = self.middle
        if len(df['Strike Price'].values) > 1:
            raise ValueError('More then one strike found')
        else:
            return df['Strike Price'].values[0]

    @property
    def strike_prices(self):
        return sorted(list(self.df['Strike Price'].unique()))

    @property
    def underlying_value(self):
        ticker = list(set(self.df['Underlying Value']))
        if len(ticker) > 1:
            raise ValueError("More than one symbol found")
        return ticker[0]

    @property
    def time_string(self):
        """ Return time in 24h string"""
        return self.time_stamp.time().strftime('%H:%M:%S')

    @property
    def date_string(self):
        """ Return date in string """
        return self.time_stamp.date().strftime('%d-%b-%Y')

    @property
    def symbol(self):
        ticker = list(set(self.df['Underlying']))
        if len(ticker) > 1:
            raise ValueError("More than one symbol found")
        return ticker[0]

    @property
    def near_expriry(self):
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.near_expiry.values)]
        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def next_expiry(self):
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.next_expiry.values)]
        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def far_expiry(self):
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.far_expiry.values)]
        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def monthly_expiry(self):
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.monthly_expiry.values)]
        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def weekly_expiry(self):
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.weekly_expiry.values)]
        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

    @property
    def current_expiry(self):
        df = self.df.loc[self.df['Expiry Date'].isin(self.expiry_dates.current_expiry.values)]
        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

    def get_by_strike(self, price, condition: str = 'equal'):
        """ Get data above or below or equal to price
        :param price: (float, int): price from which to perform action
        :param condition: (str): which condition to perform. (above, below or equal are valid)
        """
        df = None
        if condition.lower() == 'equal':
            df = OpenInterest(self.df[self.df['Strike Price'] == price])
        elif condition.lower() == 'above':
            df = OpenInterest(self.df[self.df['Strike Price'] > price])
        elif condition.lower() == 'below':
            df = OpenInterest(self.df[self.df['Strike Price'] < price])
        df.time_stamp = self.time_stamp
        return df

    def get_by_expiry(self, expiry_date: Union[datetime, str]):
        """ To get only data of selected expiry date

        :param expiry_date: (datetime) get all data of data
        :return OIObj
        """

        if isinstance(expiry_date, str):
            expiry_date = datetime.strptime(expiry_date, '%d-%m-%y')

        if not isinstance(expiry_date, datetime):
            raise TypeError('expiry_date must be datetime')

        df = self.df[self.df['Expiry Date'] == expiry_date]

        if len(df) <= 0:
            expiry_date = min(pd.to_datetime(self.df['Expiry Date'], dayfirst=True)).date().strftime('%d-%m-%y')
            df = self.df[self.df['Expiry Date'] == expiry_date]

        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

    def trim(self, strikes: int = 5):
        """ Will trim data to above and below strike from underling value
        :param strikes: int: default 5
        :return OpenInerest
        """
        df = self.df.iloc[(self.df['Strike Price'] - self.underlying_value).abs().argsort()[:strikes * 2]]
        df = OpenInterest(df)
        df.time_stamp = self.time_stamp
        return df

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
        self.symbols = pd.DataFrame()

    def get_prev_close(self, symbol):
        data = self.symbols[self.symbols['symbol'] == symbol]['previousClose']
        if data.empty:
            raise KeyError('{} not in symbols'.format(data))
        else:
            return float(data.values[0])

    def get_stocks(self) -> list:
        """ Get sorted stock list of indices

        :return: list
        """
        df = self.symbols.loc[self.symbols['priority'] == 0]
        df.sort_values(['identifier'], ascending=bool, inplace=True)
        return list(df['symbol'])

    def get_indices(self) -> list:
        """ Get sorted indices list of indices

        :return: list
        """
        df = self.symbols.loc[self.symbols['priority'] == 1]
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
        if self.symbols.empty:
            self.symbols = pd.DataFrame(data['data'])
        else:
            # Append Data to symbols
            df = self.prepare_data(data['data'])
            self.symbols = self.symbols.append(df, ignore_index=True)

        # Replace index symbol
        index_name = data['metadata']['indexName']

        # Drop meta column. Meta column has dict. Which cause TypeError in drop_duplicates
        self.symbols.drop(['meta'], axis=1, inplace=True)
        self.symbols.drop_duplicates(inplace=True)

        self.symbols.symbol[self.symbols.symbol == index_name] = c.NAME_TO_INDICES[index_name]
        self.symbols.sort_values(['identifier'], ascending=bool)
        return self


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
