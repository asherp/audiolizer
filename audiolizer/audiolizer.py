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

audiolizer_temp_dir = os.environ.get('AUDIOLIZER_TEMP', './history/')
print('audiolizer temp data:', audiolizer_temp_dir)

granularity = 300 # seconds

start_date = pd.to_datetime('2021-01-01-00-00')
ticker = 'BTC-USD'


# +
def get_history(ticker, start_date, end_date = None, granularity=granularity):
    start_date = pd.to_datetime(start_date).tz_localize(None)
    
    today = pd.Timestamp.now().tz_localize(None)
    if end_date is None:
        end_date = today
    else:
        end_date = min(today, pd.to_datetime(end_date).tz_localize(None))
        
    fnames = []
    for int_ in pd.interval_range(start_date,
                                  end_date):
        fname = audiolizer_temp_dir + '/{}-{}.csv'.format(
            ticker, int_.left.strftime('%Y-%m-%d'))

        if not os.path.exists(fname):
            int_df = HistoricalData(ticker,
                                     granularity,
                                     int_.left.strftime('%Y-%m-%d-%H-%M'),
                                     int_.right.strftime('%Y-%m-%d-%H-%M'),
                                     ).retrieve_data()
            int_df.to_csv(fname)
        fnames.append(fname)
    return pd.concat(map(lambda file: pd.read_csv(file,index_col='time', parse_dates=True),
                         fnames)).drop_duplicates()


new = get_history(ticker, start_date)
new

# +
import audiogen_p3
import itertools
import sys

def beeper(freq, amplitude = 1):
    return (amplitude*_ for _ in audiogen_p3.beep(freq))

try:
    audiogen_p3.sampler.play(itertools.chain(
        *[beeper(100*(1+i), 1./(1+i)) for i in range(8)]
    ))
except:
    print('could not play sampler')
    pass
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
                        side='right'),
                    dragmode='select',
                   ))



# -

from psidash.psidash import get_callbacks, load_conf, load_dash, load_components

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

def get_beats(start, end, freq):
    return len(pd.date_range(pd.to_datetime(start),
                             pd.to_datetime(end) + pd.Timedelta(freq),
                             freq=freq, closed=None,
                             ))


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
def play(start, end, cadence, log_freq_range, mode, drop_quantile, beat_quantile, tempo, toggle_merge, silence, selectedData):

    new = get_history(ticker, start, end)
    start_, end_ = new.index[[0, -1]]

    if toggle_merge:
        merged = 'merged'
    else:
        merged = ''
    if silence:
        silences = 'rests'
    else:
        silences = ''
        
    fname = 'BTC_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}.wav'.format(
        start_.date(),
        end_.date(),
        cadence,
        *['{}'.format(pitch(10**_).replace('#','sharp')) for _ in log_freq_range],
        mode,
        drop_quantile,
        beat_quantile,
        '{}bpm'.format(tempo),
        merged,
        silences,
    )
    
    duration = 60./tempo # length of the beat in seconds (tempo in beats per minute)
    
    play_time=''
    
    if selectedData is not None:
        start_select, end_select = selectedData['range']['x']
        # need the number of beats from beginning to start_select
        start_time = duration*(get_beats(start_, start_select, cadence)-1)
        # number of beats from beginning to end_select
        end_time = duration*(get_beats(start_, end_select, cadence)-1)
        total_time = duration*(get_beats(start_, end_, cadence)-1)
#         print('selected start, end time, total time:', start_time, end_time, total_time)
        play_time='#t={},{}'.format(start_time, end_time)
#         print(start_select, end_select, play_time)
    
    new_ = refactor(new[start_:end_], cadence)
    
    if os.path.exists(fname):
        return candlestick_plot(new_), app.get_asset_url(fname)+play_time
    
    
    
#     assert get_beats(*new_.index[[0,-1]], cadence) == len(new_)
    
    max_vol = new_.volume.max() # normalizes peak amplitude
    min_close = new_.close.min() # sets lower frequency bound
    max_close = new_.close.max() # sets upper frequency bound
    
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
 
    return candlestick_plot(new_), app.get_asset_url(fname)+play_time
    

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8051, mode='external', debug=True, dev_tools_hot_reload=False)
# -

