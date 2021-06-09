# ---
# jupyter:
#   jupytext:
#     formats: py:light
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

import pandas as pd
import numpy as np
import os

from Historic_Crypto import HistoricalData

start_date = pd.to_datetime('2021-01-01-00-00')

start_date.strftime('%Y-%m-%d-%H-%M')

# +
# new = HistoricalData('BTC-USD', 300, '2021-01-01-00-00').retrieve_data()

# new.to_csv('temp.csv')
# -

import pandas as pd
new = pd.read_csv('temp.csv', index_col='time', parse_dates=True)

new.tail()

import numpy as np

# +
import audiogen_p3
import itertools
import sys

def beeper(freq, amplitude = 1):
    return (amplitude*_ for _ in audiogen_p3.beep(freq))

audiogen_p3.sampler.play(itertools.chain(
    *[beeper(100*(1+i), 1./(1+i)) for i in range(8)]
))
# -

import dash_html_components as html

from psidash.psidash import load_app

import dash_core_components as dcc

from datetime import datetime

import plotly.graph_objs as go


# +
def refactor(df, frequency = '1W'):
    low = df.low.groupby(pd.Grouper(freq=frequency)).min()
    
    high = df.high.groupby(pd.Grouper(freq=frequency)).max()
    
    close = df.close.groupby(pd.Grouper(freq=frequency)).last()
    
    open_ = df.open.groupby(pd.Grouper(freq=frequency)).first()
    
    volume = df.volume.groupby(pd.Grouper(freq=frequency)).sum()
    
    return pd.DataFrame(dict(low=low, high=high, open=open_, close=close, volume=volume))

def candlestick_plot(df):    
    return go.Figure(data=[
        go.Bar(
            x=df.index,
            y=df.volume,
            marker_color='rgba(158,202,225,.5)',
            yaxis='y2'),
        go.Candlestick(
            x=df.index,
            open=df.open,
            high=df.high,
            low=df.low,
            close=df.close),
        ],
        
        layout=dict(yaxis=dict(title='BTC price [USD]'),
                    yaxis2=dict(
                        title='BTC volume [BTC]',
                        overlaying = 'y',
                        side='right')
                   ))

new_ = refactor(new)
candlestick_plot(new_)
# -

from psidash.psidash import get_callbacks, load_conf, load_dash, load_components

new.tail()

A0 = np.log10(27.5)
C2 = np.log10(65.40639)
C3 = np.log10(130.8128)
C4 = np.log10(262)
C5 = np.log10(523.2511)
C6 = np.log10(1046.502)
C7 = np.log10(2093.005)
C8 = np.log10(4186) # high C on piano

frequency_marks = {
    A0: 'A0',
    C2: 'C2',
    C3: 'C3',
    C4: 'C4',
    C5: 'C5',
    C6: 'C6',
    C7: 'C7',
    C8: 'C8',
}
frequency_marks

# +
conf = load_conf('../audiolizer.yaml')
app = load_dash(__name__, conf['app'], conf.get('import'))
app.layout = load_components(conf['layout'], conf.get('import'))

if 'callbacks' in conf:
    callbacks = get_callbacks(app, conf['callbacks'])


@callbacks.candlestick
def update_graph(start, end, frequency):
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    
    new_ = new[start:end]
    return candlestick_plot(refactor(new_, frequency))

def beeper(freq, amplitude=1):
    return (amplitude*_ for _ in audiogen_p3.beep(freq))

def get_frequency(price, min_price, max_price, log_frequency_range):
    return np.interp(price, [min_price, max_price], [10**_ for _ in log_frequency_range])

@callbacks.slider_marks
def update_marks(url):
    return frequency_marks

@callbacks.play
def play(start, end, cadence, log_freq_range):
    start_ = pd.to_datetime(start)
    
    if end is not None:
        end_ = pd.to_datetime(end)
    else:
        end_ = new.iloc[-1].name

    fname = 'BTC_{}_{}_{}_{}_{}.wav'.format(
        start, end_.date(), cadence, *['{}'.format(int(10**_)) for _ in log_freq_range])
    
    if os.path.exists(fname):
        return app.get_asset_url(fname)
    
    new_ = refactor(new[start_:end_], cadence)
    
    max_vol = new_.volume.max()
    min_close = new_.close.min()
    max_close = new_.close.max()

    
    with open('assets/'+fname, "wb") as f:
        audiogen_p3.sampler.write_wav(
            f,
            itertools.chain(*[
                beeper(get_frequency(close_, min_close, max_close, log_freq_range),
                       volume_/max_vol) for close_, volume_ in new_[['close', 'volume']].values]))
    return app.get_asset_url(fname)
    

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, mode='external', debug=True, dev_tools_hot_reload=False)
# -

from dash_audio_components import DashAudioComponents

# +
# DashAudioComponents?
# -

# Borrowed from John D. Cook https://www.johndcook.com/blog/2016/02/10/musical-pitch-notation/
#
# Given an input frequency, we can calculate a pitch. 

# +
from math import log2, pow

A4 = 440
C0 = A4*pow(2, -4.75)
name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    
def pitch(freq):
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)


# -

pitch(C0)


