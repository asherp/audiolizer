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

# +
import logging
logging.basicConfig(filename='audiolizer.log')
logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

logger.info("hey")
# -

import pandas as pd
import numpy as np
import os
from plotly.offline import plot

from history import get_history, get_today_GMT

# +
from dash.exceptions import PreventUpdate

from Historic_Crypto import Cryptocurrencies

import flask

data = Cryptocurrencies(coin_search = '', extended_output=True).find_crypto_pairs()
# -

crypto_dict = {}
for base, group in data.groupby('base_currency'):
    crypto_dict[base] = list(group.quote_currency.unique())

import os
import pandas as pd

from midiutil import MIDIFile

audiolizer_temp_dir = os.environ.get('AUDIOLIZER_TEMP', './history/')
logger.info('audiolizer temp data:{}'.format(audiolizer_temp_dir))
granularity = int(os.environ.get('AUDIOLIZER_GRANULARITY', 300)) # seconds

# wav_threshold, midi_threshold, price_threshold,
wav_threshold = int(os.environ.get('AUDIOLIZER_WAV_CACHE_SIZE', 100)) # megabytes
midi_threshold = int(os.environ.get('AUDIOLIZER_MIDI_CACHE_SIZE', 10))
price_threshold = int(os.environ.get('AUDIOLIZER_PRICE_CACHE_SIZE', 100))

logger.info('cache sizes: \n wav:{}Mb\n midi:{}Mb\n price:{}Mb'.format(wav_threshold, midi_threshold, price_threshold))

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
    logger.warning('could not play sampler')
    pass
# -

import dash_html_components as html

from psidash.psidash import load_app

import dash_core_components as dcc

from datetime import datetime

import plotly.graph_objs as go


# +
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

def candlestick_plot(df, base, quote):
    return go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df.open,
            high=df.high,
            low=df.low,
            close=df.close,
            showlegend=False),
        go.Bar(
            x=df.index,
            y=df.volume,
            marker_color='rgba(158,202,225,.5)',
            yaxis='y2',
            showlegend=False,
        ),
        ],
        layout=dict(yaxis=dict(title='{} price [{}]'.format(base, quote)),
                    yaxis2=dict(
                        title='{base} volume [{base}]'.format(base=base),
                        overlaying = 'y',
                        side='right'),
                    dragmode='select',
                    margin=dict(l=5, r=5, t=10, b=10),
                   ))

def write_plot(fig, fname):
    plot_div = plot(fig, output_type='div', include_plotlyjs='cdn')
    with open(fname, 'w') as f:
        f.write(plot_div)
        f.write('\n')


# -

from psidash.psidash import get_callbacks, load_conf, load_dash, load_components, assign_callbacks

# +
A4 = 440 # tuning
C0 = A4*pow(2, -4.75)

frequencies = dict(
#     A4 = A4,
#     C0 = C0,
    A0=27.5,
    C2=65.40639,
    C3=130.8128,
    C4=262,
    C5=523.2511,
    C6=1046.502,
    C7=2093.005,
    C8=4186, # high C on piano
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
                # todo: use moving average
                merged[-1][1] = (amp + last_amp)/2
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
def freq_to_degrees(freq):
    """convert input frequency to midi degree standard

    midi degrees are in the range [0, 127]
    """
    return min(127, max(0, int(69+np.floor(12*np.log2(freq/440.)))))

def write_midi(beeps, tempo, fname, time=0, track=0, channel=0):
    # duration = 60/tempo
    midi_file = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                          # automatically)
    beat_duration = 60./tempo

    midi_file.addTempo(track, time, tempo)

    for freq, amp, dur in beeps: # Hz, [0,1], sec            
        pitch = freq_to_degrees(freq) # MIDI note number
        duration = dur/beat_duration # convert from seconds to beats
        volume = min(127, int(amp*127))  # 0-127, as per the MIDI standard
        midi_file.addNote(track, channel, pitch, time, duration, volume)
        time += duration
    with open(fname, "wb") as output_file:
        midi_file.writeFile(output_file)


# +
import glob
from collections import defaultdict

def get_files(fname_glob="assets/*.wav"):
    """retrieve files and metadata"""
    fnames = glob.glob(fname_glob)
    results = defaultdict(list)
    for fname in fnames:
        results['fname'].append(fname)
        results['size'].append(os.path.getsize(fname))
        results['accessed'].append(datetime.fromtimestamp(os.path.getatime(fname)))
    if len(results) > 0:
        files = pd.DataFrame(results).set_index('accessed').sort_index(ascending=False)
        files['cumulative'] = files['size'].cumsum()
        return files

def clear_files(fname_glob="assets/*.wav", max_storage=10e6):
    """keep files up to a maximum in storage size (bytes)"""
    files = get_files(fname_glob)
    if files is not None:
        removable = files[files.cumulative > max_storage].fname.values
        for fname in removable:
            if os.path.exists(fname):
                os.remove(fname)
        return removable
    return []


# +

conf = load_conf('../audiolizer.yaml')

# app = dash.Dash(__name__, server=server) # call flask server

import dash

server = flask.Flask(__name__) # define flask app.server

conf['app']['server'] = server

app = load_dash(__name__, conf['app'], conf.get('import'))

# app = dash.Dash(__name__, server=server) # call flask server

# app = dash.Dash(__name__, server=server) # how we need to initialize

app.layout = load_components(conf['layout'], conf.get('import'))

if 'callbacks' in conf:
    callbacks = get_callbacks(app, conf['callbacks'])
    assign_callbacks(callbacks, conf['callbacks'])

def beeper(freq, amplitude=1, duration=.25):
    return (amplitude*_ for _ in audiogen_p3.beep(freq, duration))

def get_frequency(price, min_price, max_price, log_frequency_range):
    return np.interp(price, [min_price, max_price], [10**_ for _ in log_frequency_range])

@callbacks.update_base_options
def update_base_options(url):
    return [{'label': base, 'value': base} for base in crypto_dict]

@callbacks.update_quote_options
def update_quote_options(base, quote_prev):
    quotes = crypto_dict[base]
    options = [{'label': quote, 'value': quote} for quote in quotes]
    if quote_prev in quotes:
        quote = quote_prev
    else:
        quote = quotes[0]
    return quote, options

@callbacks.slider_marks
def update_marks(url):
    return frequency_marks

@callbacks.update_date_range
def update_date_range(date_select,
    # timezone
    ):
    period, cadence = date_select.split('-')
    today = get_today_GMT().tz_localize('GMT') #.tz_convert(timezone)
    logger.info('Period was {}'.format(period))
    start_date = (today-pd.Timedelta(period)).strftime('%Y-%m-%d')
#     end_date = (today+pd.Timedelta('1d')).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    date_range_start = start_date
    date_range_end = end_date
    initial_visible_month = start_date
    return date_range_start, date_range_end, cadence, initial_visible_month

@callbacks.play
def play(base, quote, start, end, cadence, log_freq_range,
         mode, drop_quantile, beat_quantile,
         tempo, toggle_merge, silence,
         selectedData,
         # wav_threshold, midi_threshold, price_threshold,
         price_type,
         # timezone,
         ):
    # logger.info('timezone = {}'.format(timezone))
    ticker = '{}-{}'.format(base, quote)
    logger.info('ticker: {}'.format(ticker))
    cleared = clear_files('assets/*.wav', max_storage=wav_threshold*1e6)
    if len(cleared) > 0:
        logger.info('cleared {} wav files'.format(len(cleared)))
    cleared = clear_files('assets/*.midi', max_storage=midi_threshold*1e6)
    if len(cleared) > 0:
        logger.info('cleared {} midi files'.format(len(cleared)))
    cleared = clear_files('history/*.csv.gz', max_storage=price_threshold*1e6)
    if len(cleared) > 0:
        logger.info('cleared {} price files'.format(len(cleared)))
    logger.info('start, end {} {}'.format(start, end))
    try:
        # new = get_history(ticker, timezone, start, end)
        new = get_history(ticker, start, end)
    except:
        logger.info('cannot get history for {} {} {}'.format(ticker, start, end))
        raise
    start_, end_ = new.index[[0, -1]]

    if (end_-start_).days == 1:
        # make sure we get exactly 24 hrs of data
        logger.info('make sure we get exactly 24 hrs of data')
        start_ = end_ - pd.Timedelta('1d')

    if toggle_merge:
        merged = 'merged'
    else:
        merged = ''
    if silence:
        silences = 'rests'
    else:
        silences = ''

    fname = '{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}_{}.wav'.format(
        ticker,
        price_type,
        start_.date(),
        end_.date(),
        cadence,
        *['{}'.format(pitch(10**_).replace('#', 'sharp')) for _ in log_freq_range],
        mode,
        drop_quantile,
        beat_quantile,
        '{}bpm'.format(tempo),
        merged,
        silences,
    )

    midi_file = fname.split('.wav')[0] + '.midi'

    duration = 60./tempo # length of the beat in seconds (tempo in beats per minute)

    play_time = ''

    if selectedData is not None:
        start_select, end_select = selectedData['range']['x']
        # need the number of beats from beginning to start_select
        start_time = duration*(get_beats(start_, start_select, cadence)-1)
        # number of beats from beginning to end_select
        end_time = duration*(get_beats(start_, end_select, cadence)-1)
        total_time = duration*(get_beats(start_, end_, cadence)-1)
#         logger.info('selected start, end time, total time:', start_time, end_time, total_time)
        play_time = '#t={},{}'.format(start_time, end_time)
#         logger.info(start_select, end_select, play_time)

    new_ = refactor(new[start_:end_], cadence)
    logger.info('{}->{}'.format(*new_.index[[0,-1]]))
    
    midi_asset = app.get_asset_url(midi_file)

    if os.path.exists(fname):
        return (candlestick_plot(new_, base, quote),
                app.get_asset_url(fname)+play_time, midi_asset, midi_asset, midi_asset)

#     assert get_beats(*new_.index[[0,-1]], cadence) == len(new_)

    max_vol = new_.volume.max() # normalizes peak amplitude
    min_price = new_[price_type].min() # sets lower frequency bound
    max_price = new_[price_type].max() # sets upper frequency bound

    amp_min = beat_quantile/100 # threshold amplitude to merge beats
    min_vol = new_.volume.quantile(drop_quantile/100)

    beeps = []
    for t, (price, volume_) in new_[[price_type, 'volume']].iterrows():
        if ~np.isnan(price):
            freq_ = get_frequency(price, min_price, max_price, log_freq_range)
            if mode == 'tone':
                pass
            elif mode == 'pitch':
                freq_ = freq(pitch(freq_))
            else:
                raise NotImplementedError(mode)
            beep = freq_, volume_/max_vol, duration
            beeps.append(beep)
        else:
            freq_ = get_frequency(min_price, min_price, max_price, log_freq_range)
            beep = freq_, 0, duration
            beeps.append(beep)
            logger.warning('found nan price {}, {}, {}'.format(t, price, volume_))
    if mode == 'pitch':
        if toggle_merge:
            beeps = merge_pitches(beeps, amp_min)
        if silence:
            beeps = quiet(beeps, min_vol/max_vol)

#     logger.info(mode, 'unique frequencies:', len(np.unique([_[0] for _ in beeps])))

    audio = [beeper(*beep) for beep in beeps]

    with open('assets/'+fname, "wb") as f:
        audiogen_p3.sampler.write_wav(f, itertools.chain(*audio))


    write_midi(beeps, tempo, 'assets/' + midi_file)

    return (candlestick_plot(new_, base, quote),
            app.get_asset_url(fname)+play_time, midi_asset, midi_asset, '')

server = app.server


if __name__ == '__main__':
    app.run_server(
        host=conf['run_server']['host'],
        port=conf['run_server']['port'],
        mode='external',
        debug=True,
        dev_tools_hot_reload=False,
        extra_files=['../audiolizer.yaml']
        )
# -


