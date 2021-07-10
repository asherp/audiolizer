# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# Objective: get_history should fetch all the data at once then save it to separate files.

# +
from Historic_Crypto import HistoricalData
import pandas as pd
import os

granularity = int(os.environ.get('AUDIOLIZER_GRANULARITY', 300)) # seconds

audiolizer_temp_dir = os.environ.get('AUDIOLIZER_TEMP', './history/')
print('audiolizer temp data:', audiolizer_temp_dir)


def refactor(df, frequency='1W'):
    """Refactor/rebin the data to a lower cadence

    The data is regrouped using pd.Grouper
    """
    low = df.low.groupby(pd.Grouper(freq=frequency)).min()
    high = df.high.groupby(pd.Grouper(freq=frequency)).max()
    close = df.close.groupby(pd.Grouper(freq=frequency)).last()
    open_ = df.open.groupby(pd.Grouper(freq=frequency)).first()
    volume = df.volume.groupby(pd.Grouper(freq=frequency)).sum()
    return pd.DataFrame(dict(low=low, high=high, open=open_, close=close, volume=volume))


def load_date(ticker, granularity, int_):
    start_ = int_.left.strftime('%Y-%m-%d-%H-%M')
    end_ = int_.right.strftime('%Y-%m-%d-%H-%M')
    try:
        return HistoricalData(ticker,
                              granularity,
                              start_,
                              end_,
                              ).retrieve_data()
    except:
        print('could not load using {} {}'.format(start_, end_))
        raise


def get_gaps(df, granularity):
    new_ = refactor(df, '{}s'.format(granularity))
    return new_[new_.close.isna()]


def fetch_data(ticker, granularity, start_, end_):
    """Need dates in this format %Y-%m-%d-%H-%M"""
    try:
        return HistoricalData(ticker,
                              granularity,
                              start_,
                              end_,
                              ).retrieve_data()
    except:
        print('could not load using {} {}'.format(start_, end_))
        raise


def write_data(df, ticker):
    for t, day in df.groupby(pd.Grouper(freq='1D')):
        tstr = t.strftime('%Y-%m-%d-%H-%M')
        fname = audiolizer_temp_dir + '/{}-{}.csv.gz'.format(
                ticker, t.strftime('%Y-%m-%d'))
        if len(day) > 1:
            day.to_csv(fname, compression='gzip')
            print('wrote {}'.format(fname))
        
def fetch_missing(files_status, ticker, granularity):
    """Iterate over batches of missing dates"""
    for batch, g in files_status[files_status.found==0].groupby('batch', sort=False):
        t1, t2 = g.iloc[[0, -1]].index
        # extend by 1 day whether or not t1 == t2
        t2 += pd.Timedelta('1D')
        endpoints = [t.strftime('%Y-%m-%d-%H-%M') for t in [t1, t2]]
        print('fetching {}, {}'.format(len(g), endpoints))
        df = fetch_data(ticker, granularity, *endpoints)
        write_data(df, ticker)

def get_history(ticker, start_date, end_date = None, granularity=granularity):
    """Fetch/load historical data from Coinbase API at specified granularity
    
    Data loaded from start_date through end of end_date
    params:
        start_date: (str) (see pandas.to_datetime for acceptable formats)
        end_date: (str)
        granularity: (int) seconds (default: 300)

    price data is saved by ticker and date and stored in audiolizer_temp_dir
    """
    start_date = pd.to_datetime(start_date).tz_localize(None)
    
    today = pd.Timestamp.now().tz_localize(None)
    if end_date is None:
        end_date = today + pd.Timedelta('1D')
    else:
        end_date = min(today, pd.to_datetime(end_date).tz_localize(None)) + pd.Timedelta('1D')
        
    fnames = []
    foundlings = []
    dates = []
    batch = []
    batch_number = 0
    last_found = -1
    for int_ in pd.interval_range(start_date, end_date):
        dates.append(int_.left)
        fname = audiolizer_temp_dir + '/{}-{}.csv.gz'.format(
            ticker, int_.left.strftime('%Y-%m-%d'))
        found = int(os.path.exists(fname))
        foundlings.append(found)
        if found != last_found:
            batch_number += 1
        last_found = found
        batch.append(batch_number)
        fnames.append(fname)
    
    
    files_status = pd.DataFrame(dict(files=fnames, found=foundlings, batch=batch), index=dates)
    fetch_missing(files_status, ticker, granularity)

    df = pd.concat(map(lambda file: pd.read_csv(file, index_col='time', parse_dates=True),
                         fnames)).drop_duplicates()
    gaps = get_gaps(df, granularity)

    if len(gaps) > 0:
        print('found {} data gaps'.format(len(gaps)))
        # fetch the data for each date
        for start_date in gaps.groupby(pd.Grouper(freq='1d')).first().index:
            print('\tfetching {}'.format(start_date))
            int_ = pd.interval_range(start=start_date, periods=1, freq='1d')
            int_ = pd.Interval(int_.left[0], int_.right[0])
            int_df = load_date(ticker, granularity, int_)
            fname = audiolizer_temp_dir + '/{}-{}.csv.gz'.format(
                ticker, int_.left.strftime('%Y-%m-%d'))
            int_df.to_csv(fname, compression='gzip')

    df = pd.concat(map(lambda file: pd.read_csv(file,index_col='time', parse_dates=True, compression='gzip'),
                         fnames)).drop_duplicates()
    return df


# + active="ipynb"
# hist = get_history('BTC-USD', '2020-04-20', '2020-05-18')
# hist
# -

# !jupytext --sync history.ipynb
