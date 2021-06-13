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

from dash.exceptions import PreventUpdate

from Historic_Crypto import HistoricalData

import os
import pandas as pd

audiolizer_temp_dir = os.environ.get('AUDIOLIZER_TEMP', './')
audiolizer_temp_dir

granularity = 300 # seconds

start_date = pd.to_datetime('2021-01-01-00-00')
ticker = 'BTC-USD'


# +
def get_history(ticker, start_date):
    default_history = audiolizer_temp_dir + '/{}.csv'.format(ticker)

    if os.path.exists(default_history):
        new = pd.read_csv(default_history, index_col='time', parse_dates=True)
    else:
        new = HistoricalData(ticker,
                             granularity,
                             start_date.strftime('%Y-%m-%d-%H-%M')
                            ).retrieve_data()
        new.to_csv(default_history)
    return new

new = get_history(ticker, start_date)

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

# +
A4 = 440 # tuning
C0 = A4*pow(2, -4.75)

frequencies = dict(
#     A4 = A4,
#     C0 = C0,
    A0 = 27.5,
    C2 = 65.40639,
    C3 = 130.8128,
    C4 = 262,
    C5 = 523.2511,
    C6 = 1046.502,
    C7 = 2093.005,
    C8 = 4186, # high C on piano
)
# -

frequency_marks = {np.log10(v): k for k,v in frequencies.items()}
frequency_marks

# +
from math import log2

def pitch(freq):
    """convert from frequency to pitch
    
    Borrowed from John D. Cook https://www.johndcook.com/blog/2016/02/10/musical-pitch-notation/
    """
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)

def freq(note, A4=A4):
    """ convert from pitch to frequency
    
    based on https://gist.github.com/CGrassin/26a1fdf4fc5de788da9b376ff717516e
    """
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

    octave = int(note[2]) if len(note) == 3 else int(note[1])
        
    keyNumber = notes.index(note[0:-1]);
    
    if (keyNumber < 3) :
        keyNumber = keyNumber + 12 + ((octave - 1) * 12) + 1; 
    else:
        keyNumber = keyNumber + ((octave - 1) * 12) + 1; 

    return A4 * 2** ((keyNumber- 49) / 12)


# -

a = [_ for _ in range(5)]
a
for i, _ in enumerate(a):
    a[i] = 0

a


# +
def merge_pitches(beeps, amp_min):
    merged = []
    last_freq = 0
    last_amp = 0
    for freq, amp, dur in beeps:
        if freq == last_freq:
            if merged[-1][1] < amp_min:
                merged[-1][1] = (amp + last_amp)/2 # todo: use moving average
                merged[-1][2] += dur
            continue
        merged.append([freq, amp, dur])
        last_freq = freq
        last_amp = amp
    return merged

def quiet(beeps, min_amp):
    silenced = []
    for freq, amp, dur in beeps:
        if amp < min_amp:
            amp = 0
        silenced.append((freq, amp, dur))
    return silenced        


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

def beeper(freq, amplitude=1, duration=.25):
    return (amplitude*_ for _ in audiogen_p3.beep(freq, duration))

def get_frequency(price, min_price, max_price, log_frequency_range):
    return np.interp(price, [min_price, max_price], [10**_ for _ in log_frequency_range])

@callbacks.slider_marks
def update_marks(url):
    return frequency_marks

@callbacks.play
def play(start, end, cadence, log_freq_range, mode, drop_quantile, beat_quantile, toggle_merge, silence):
    start_ = pd.to_datetime(start)
    if end is not None:
        end_ = pd.to_datetime(end)
    else:
        end_ = new.iloc[-1].name

    if toggle_merge:
        merged = 'merged'
    else:
        merged = ''
    if silence:
        silences = 'rests'
    else:
        silences = ''
        
    fname = 'BTC_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}.wav'.format(
        start,
        end_.date(),
        cadence,
        *['{}'.format(pitch(10**_).replace('#','sharp')) for _ in log_freq_range],
        mode,
        drop_quantile,
        beat_quantile,
        merged,
        silences,
    )
    
    if os.path.exists(fname):
        return app.get_asset_url(fname)
    
    new_ = refactor(new[start_:end_], cadence)
    
    max_vol = new_.volume.max() # normalizes peak amplitude
    min_close = new_.close.min() # sets lower frequency bound
    max_close = new_.close.max() # sets upper frequency bound
    duration = .25 # length of the beat in seconds
    amp_min = beat_quantile/100 # threshold amplitude to merge beats
    min_vol = new_.volume.quantile(drop_quantile/100)
    
    if mode == 'tone':
        beeps = [(get_frequency(close_, min_close, max_close, log_freq_range),
                  volume_/max_vol,
                  duration) for close_, volume_ in new_[['close', 'volume']].values]
        
    elif mode == 'pitch':
        beeps = [(freq(pitch(get_frequency(close_, min_close, max_close, log_freq_range))),
                  volume_/max_vol,
                  duration) for close_, volume_ in new_[['close', 'volume']].values]
        if toggle_merge:
            beeps = merge_pitches(beeps, amp_min)
        if silence:
            beeps = quiet(beeps, min_vol/max_vol)
        
#     print(mode, 'unique frequencies:', len(np.unique([_[0] for _ in beeps])))
        
    audio = [beeper(*beep) for beep in beeps]
    
    with open('assets/'+fname, "wb") as f:
        audiogen_p3.sampler.write_wav(f, itertools.chain(*audio))
    return app.get_asset_url(fname)
    

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, mode='external', debug=True, dev_tools_hot_reload=False)
# -
# ls


