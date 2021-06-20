The Market Audiolizer takes market price and volume data and maps it onto a musical scale. In other words, it turns prices into melodies. In this way, market analysis may be approached from the standpoint of music theory, which may be more intuitive for the listener than charts are to the trader. From the standpoint of accessibility, audiolization allows vital market information to be accessible to those with visual impairment.


## Temp directories

Before we get started, we'll need to tell the audiolizer where it can cache price data. Set the `AUDIOLIZER_TEMP` environment variable.

```python
import os
os.environ['AUDIOLIZER_TEMP'] = '/tmp/price_data'
```

## Loading BTC price

```python
from audiolizer.audiolizer import get_history
ticker='BTC-USD'
btc = get_history(ticker, 'June 1, 2021', 'June 18, 2021', 300)
btc.head()
```

| time                |     low |    high |    open |   close |   volume |
|:--------------------|--------:|--------:|--------:|--------:|---------:|
| 2021-06-01 00:00:00 | 37140.9 | 37639.9 | 37276.2 | 37624.1 |  125.973 |
| 2021-06-01 00:05:00 | 37532.8 | 37717.5 | 37627.2 | 37572.9 |  177.163 |
| 2021-06-01 00:10:00 | 37546.2 | 37670.3 | 37572.8 | 37561.7 |  185.647 |
| 2021-06-01 00:15:00 | 37510.7 | 37643.8 | 37566.4 | 37513.7 |  157.127 |
| 2021-06-01 00:20:00 | 37505   | 37694.8 | 37510.7 | 37647.7 |  121.479 |


<details> <summary> help(get_history) </summary>
    
```console
Help on function get_history in module audiolizer.audiolizer:

get_history(ticker, start_date, end_date=None, granularity=300)
    Fetch/load historical data from Coinbase API at specified granularity
    
    params:
        start_date: (str) (see pandas.to_datetime for acceptable formats)
        end_date: (str)
        granularity: (int) seconds (default: 300)
```
</details>

We can plot this data immediately

```python
from audiolizer.audiolizer import candlestick_plot, write_plot

fig = candlestick_plot(btc.loc['June 16, 2021'])

# write plot to disk so we can include it in markdown
write_plot(fig, 'plot_div_06-16-2021_300s.html')
```

{! plot_div_06-16-2021_300s.html !}


## Rebinning price history

The above resolution may be too high to search for patterns. Let's rebin it to a lower resolution.

```python
from audiolizer.audiolizer import refactor

btc3h = refactor(btc.loc['June 16, 2021'], frequency='3h')
```

| time                |     low |    high |    open |   close |   volume |
|:--------------------|--------:|--------:|--------:|--------:|---------:|
| 2021-06-16 00:00:00 | 39612   | 40180.1 | 40158.1 | 40049.2 | 1175.11  |
| 2021-06-16 03:00:00 | 39833   | 40425   | 40046.7 | 40257.5 | 1329.77  |
| 2021-06-16 06:00:00 | 39930   | 40499   | 40261.8 | 40048.2 |  945.778 |
| 2021-06-16 09:00:00 | 38929.2 | 40187.1 | 40048.2 | 39098.9 | 1697.73  |
| 2021-06-16 12:00:00 | 38659.7 | 39518.1 | 39092.7 | 38854.5 | 2639.68  |
| 2021-06-16 15:00:00 | 38443   | 39310   | 38854.5 | 39180   | 2867.48  |
| 2021-06-16 18:00:00 | 38328.2 | 39706.6 | 39180   | 38533.5 | 4495.34  |
| 2021-06-16 21:00:00 | 38105   | 38927.9 | 38527.5 | 38351   | 2087.69  |

```python
fig = candlestick_plot(btc3h)

# write plot to disk so we can include it in markdown
write_plot(fig, 'plot_div_06-16-2021_3h.html')
```

{! plot_div_06-16-2021_3h.html !}


## From price to frequency

Now that we have a more managable price history, we're ready to start audiolizing. We start with a simple linear map between price and frequency. The min/max price closing price is scaled to min and max pitches.

```python
from audiolizer.audiolizer import frequencies, get_frequency
import numpy as np

C2_log = np.log10(frequencies['C2'])
C3_log = np.log10(frequencies['C3'])

btc3h['frequency'] = get_frequency(
    btc3h.close.values,
    btc3h.close.min(),
    btc3h.close.values.max(),
    [C2_log, C3_log])
# btc3h[['close', 'frequency']]
```

| time                |   close |   frequency |
|:--------------------|--------:|------------:|
| 2021-06-16 00:00:00 | 40049.2 |    123.664  |
| 2021-06-16 03:00:00 | 40257.5 |    130.813  |
| 2021-06-16 06:00:00 | 40048.2 |    123.632  |
| 2021-06-16 09:00:00 | 39098.9 |     91.0648 |
| 2021-06-16 12:00:00 | 38854.5 |     82.6796 |
| 2021-06-16 15:00:00 | 39180   |     93.8467 |
| 2021-06-16 18:00:00 | 38533.5 |     71.6676 |
| 2021-06-16 21:00:00 | 38351   |     65.4064 |


## From volume to amplitude

The amplitude of each beat will be set by volume, normalized by the maximum volume in the time range.

For the moment, the duration of each note will be fixed.

```python
duration=.25 #sec
btc3h['amplitude']=btc3h.volume/btc3h.volume.max()
btc3h['duration'] = duration
btc3h[['close', 'frequency', 'volume', 'amplitude', 'duration']]
```

```python
beeps = [(frequency,
          amplitude,
          duration) for frequency, amplitude, duration in btc3h[['frequency', 'amplitude', 'duration']].values]
```

Given our collection of beeps, we can now turn them into an audio file

```python
from audiolizer.audiolizer import beeper, audiogen_p3, itertools

audio = [beeper(*beep) for beep in beeps]
with open('beeps_tonal.wav', "wb") as f:
    audiogen_p3.sampler.write_wav(f, itertools.chain(*audio))
```

<audio controls>
  <source src="https://github.com/asherp/audiolizer/blob/master/docs/beeps_tonal.wav?raw=true" type="audio/WAV">
  Your browser does not support the audio tag.
</audio>


## From tone to pitch

So far we have produced a sequence of pure tones. Let's turn them into pitches to make them a bit easier to hear. This has the effect of rebinning the price.

```python
from audiolizer.audiolizer import pitch, freq

C4_log = np.log10(frequencies['C4'])
C5_log = np.log10(frequencies['C5'])
btc_hourly= refactor(btc.loc['June 16, 2021'].copy(), '1h')
btc_hourly['frequency'] = get_frequency(
    btc_hourly.close.values,
    btc_hourly.close.min(),
    btc_hourly.close.values.max(),
    [C4_log, C5_log])
btc_hourly['note'] = [pitch(_) for _ in btc_hourly.frequency]
btc_hourly['pitch'] = [freq(_) for _ in btc_hourly.note]
# print(btc_hourly[['close', 'frequency', 'note', 'pitch']].head().to_markdown())
```

| time                |   close |   frequency | note   |   pitch |
|:--------------------|--------:|------------:|:-------|--------:|
| 2021-06-16 00:00:00 | 39886.9 |     458.764 | A#4    | 466.164 |
| 2021-06-16 01:00:00 | 40109.4 |     487.269 | B4     | 493.883 |
| 2021-06-16 02:00:00 | 40049.2 |     479.554 | A#4    | 466.164 |
| 2021-06-16 03:00:00 | 40026   |     476.591 | A#4    | 466.164 |
| 2021-06-16 04:00:00 | 40271.8 |     508.076 | B4     | 493.883 |


## Duration

The note duration may be controlled by merging pitches that are the same based on volume. Here's our merging function:

```python
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
```

As we cycle through the stack of beeps, we check if the last beep's frequency matches the current one. If so, we check if the last beep's amplitude is above the `amp_min` threshold. If so, we set the last beep's amplitude to the average of the last and current and we increase the last beep's duration by the current beep's duration.

The point of doing this is that low amplitude indicates low (sideways) trading volume so we play a longer note, whereas high trade volume will get the minimum duration, and the melody will be "faster".

The `quiet` function is similar:

```python
def quiet(beeps, min_amp):
    silenced = []
    for freq, amp, dur in beeps:
        if amp < min_amp:
            amp = 0
        silenced.append((freq, amp, dur))
    return silenced   
```

Here we just set the amplitude to 0 if it's below the `min_amp` threshold.

```python
candlestick_plot(btc_hourly)
```

```python
max_vol = btc_hourly.volume.max()
beeps = [(pitch,
          volume/max_vol,
          duration) for pitch, volume in btc_hourly[['pitch', 'volume']].values]
beeps = quiet(merge_pitches(beeps, .25), .25)

audio = [beeper(*beep) for beep in beeps]
with open('beeps_pitch.wav', "wb") as f:
    audiogen_p3.sampler.write_wav(f, itertools.chain(*audio))
```

The following sample is an audiolization of the above candlestick plot. The first 2.5 seconds are silent since the first half of the day's trades had relatively low volume.

<audio controls>
  <source src="https://github.com/asherp/audiolizer/blob/master/docs/beeps_pitch.wav?raw=true" type="audio/WAV">
  Your browser does not support the audio tag.
</audio>
