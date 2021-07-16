# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Objective: get_history should fetch all the data at once then save it to separate files.

import logging
logging.basicConfig(filename='audiolizer.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# +
import pytz

from Historic_Crypto import HistoricalData
import pandas as pd
import os
from datetime import datetime

def get_timezones(url):
    return [dict(label=v, value=v) for v in pytz.all_timezones]


granularity = int(os.environ.get('AUDIOLIZER_GRANULARITY', 300)) # seconds

audiolizer_temp_dir = os.environ.get('AUDIOLIZER_TEMP', './history/')
logger.info('audiolizer temp data: {}'.format(audiolizer_temp_dir))

max_age = pd.Timedelta(os.environ.get('AUDIOLIZER_MAX_AGE', '5m'))
logger.info('audiolizer max daily age {}'.format(max_age))

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
    logger.info('loading single date {}'.format(int_))
    start_ = int_.left.strftime('%Y-%m-%d-%H-%M')
    end_ = int_.right.strftime('%Y-%m-%d-%H-%M')
    try:
        return HistoricalData(ticker,
                              granularity,
                              start_,
                              end_,
                              ).retrieve_data()
    except:
        logger.warning('could not load using {} {}'.format(start_, end_))
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
        logger.warning('could not load using {} {}'.format(start_, end_))
        raise


def write_data(df, ticker):
    for t, day in df.groupby(pd.Grouper(freq='1D')):
        tstr = t.strftime('%Y-%m-%d-%H-%M')
        fname = audiolizer_temp_dir + '/{}-{}.csv.gz'.format(
                ticker, t.strftime('%Y-%m-%d'))
        if len(day) > 1:
            day.to_csv(fname, compression='gzip')
            logger.info('wrote {}'.format(fname))
        
def fetch_missing(files_status, ticker, granularity):
    """Iterate over batches of missing dates"""
    for batch, g in files_status[files_status.found==0].groupby('batch', sort=False):
        t1, t2 = g.iloc[[0, -1]].index
        # extend by 1 day whether or not t1 == t2
        t2 += pd.Timedelta('1D')
        endpoints = [t.strftime('%Y-%m-%d-%H-%M') for t in [t1, t2]]
        logger.info('fetching {}, {}'.format(len(g), endpoints))
        df = fetch_data(ticker, granularity, *endpoints)
        write_data(df, ticker)

        
def get_files_status(ticker, start_date, end_date):
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
    return files_status


# + active="ipynb"
# get_files_status('BTC-USD', get_today_GMT() - pd.Timedelta('10d'), get_today_GMT())

# +
def get_today(ticker, granularity):
    today = get_today_GMT()
    tomorrow = today + pd.Timedelta('1D')
    start_ = '{}-00-00'.format(today.strftime('%Y-%m-%d'))
    end_ = today.strftime('%Y-%m-%d-%H-%M')
    try:
        return HistoricalData(ticker,
                              granularity,
                              start_,
                              end_,
                              ).retrieve_data()
    except:
        logger.warning('could not load using {} {}'.format(start_, end_))
        raise


def get_age(fname):
    """Get the age of a given a file"""
    st=os.stat(fname)    
    mtime=st.st_mtime
    return pd.Timestamp.now() - datetime.fromtimestamp(mtime)

def get_today_GMT():
    # convert from system time to GMT
    system_time = pd.Timestamp(datetime.now().astimezone())
    today = system_time.tz_convert('GMT')
    return today
        
def get_history(ticker, user_tz, start_date, end_date = None, granularity=granularity):
    """Fetch/load historical data from Coinbase API at specified granularity
    
    Data loaded from start_date through end of end_date
    params:
        start_date: (str) (see pandas.to_datetime for acceptable formats)
        end_date: (str)
        granularity: (int) seconds (default: 300)

    price data is saved by ticker and date and stored in audiolizer_temp_dir
    
    There are three timezones to keep track of!
    user timezone: the timezone the user is in (display time)
    system timezone: the timezone of the machine the audiolizer is run from
    GMT: the timezone that price history is fetched/stored in
    """
    logger.info('user timzeone: {}'.format(user_tz))
    start_date = pd.to_datetime(start_date).tz_localize(user_tz).tz_convert('GMT')

    today = get_today_GMT()

    if end_date is None:
        # don't include today
        end_date = today
    else:
        # convert the user-specified date and timezone to GMT
        end_date = pd.to_datetime(end_date).tz_localize(user_tz).tz_convert('GMT')
        # prevent queries from the future
        end_date = min(today, end_date)
    
    assert start_date < end_date
    
    logger.info('getting {} files status: {} -> {}'.format(ticker, start_date, end_date))
    files_status = get_files_status(ticker, start_date, end_date)
    fetch_missing(files_status, ticker, granularity)
    
    if len(files_status) == 0:
        raise IOError('Could not get file status for {}'.format(ticker, start_date, end_date))
        
    df = pd.concat(map(lambda file: pd.read_csv(file, index_col='time', parse_dates=True, compression='gzip'),
                         files_status.files)).drop_duplicates()


    if end_date == today:
        logger.info('end date is today!')
        # check age of today's data. If it's old, fetch the new one
        today_fname = audiolizer_temp_dir + '/{}-today.csv.gz'.format(ticker)
        if os.path.exists(today_fname):
            if get_age(today_fname) > max_age:
                logger.info('{} is too old, fetching new data'.format(today_fname))
                today_data = get_today(ticker, granularity)
                today_data.to_csv(today_fname, compression='gzip')
            else:
                logger.info('{} is not that old, loading from disk'.format(today_fname))
                today_data = pd.read_csv(today_fname, index_col='time', parse_dates=True, compression='gzip')
        else:
            logger.info('{} not present. loading'.format(today_fname))
            today_data = get_today(ticker, granularity)
            today_data.to_csv(today_fname, compression='gzip')
        df = pd.concat([df, today_data]).drop_duplicates()
    df.index = df.index.tz_localize('GMT').tz_convert(user_tz)
    return df

# + active="ipynb"
# hist = get_history('BTC-USD', 'EST',
#                    '2021-07-09',
# #                   pd.Timestamp.now().tz_localize(None)-pd.Timedelta('3D'),
#                   )
# hist

# + active="ipynb"
# from audiolizer import candlestick_plot

# + active="ipynb"
# candlestick_plot(hist, 'BTC', 'USD')
