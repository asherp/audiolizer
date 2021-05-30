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

from Historic_Crypto import HistoricalData

start_date = pd.to_datetime('2021-01-01-00-00')

start_date.strftime('%Y-%m-%d-%H-%M')



# +
# new = HistoricalData('BTC-USD', 300, '2021-01-01-00-00').retrieve_data()

# new.to_csv('temp.csv')
# -

import pandas as pd
new = pd.read_csv('temp.csv', index_col='time', parse_dates=True)

new.head()

# +
# pd.Grouper?
# -

new.groupby(pd.Grouper(freq="1W"))

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

# +
# html.Audio?
# -

from psidash.psidash import load_app

import dash_core_components as dcc

app = load_app(__name__, '../audiolizer.yaml')

callbacks.pass_through

from datetime import datetime

# +
# datetime?
# -

start = pd.to_datetime('2021-01-01')

end = pd.to_datetime('2021-01-05')

new[start:end]

import plotly.graph_objs as go


def refactor(df, frequency = '1W'):
    low = df.low.groupby(pd.Grouper(freq=frequency)).min()
    
    high = df.high.groupby(pd.Grouper(freq=frequency)).max()
    
    close = df.close.groupby(pd.Grouper(freq=frequency)).last()
    
    open_ = df.open.groupby(pd.Grouper(freq=frequency)).first()
    
    volume = df.volume.groupby(pd.Grouper(freq=frequency)).sum()
    
    return go.Figure(data=[go.Candlestick(
                x=volume.index,
                open=open_,
                high=high,
                low=low,
                close=close)])


refactor(new)

from psidash.psidash import get_callbacks, load_conf, load_dash, load_components

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
    
    return refactor(new_, frequency)

def beeper(freq, amplitude = 1):
    return (amplitude*_ for _ in audiogen_p3.beep(freq))



@callbacks.play
def play(start, end, frequency, play_button):
    print('playing')
    audiogen_p3.sampler.play(itertools.chain(
        *[beeper(100*(1+i), 1./(1+i)) for i in range(8)]
    ))
    return 'playing {}'.format(frequency)
    

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, mode='external', debug=True)
# -




