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

btc = get_history('BTC-USD', 'June 1, 2021', 'June 18, 2021', 300)
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


## Rebinning price dada

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


## From Price to frequency

Now that we have a more managable price history, we're ready to start audiolizing.

```python
from audiolizer.audiolizer import frequencies, get_frequency
```

```python
C2_log = np.log10(frequencies['C2'])
C3_log = np.log10(frequencies['C3'])
```

```python
def get_frequency(price, min_price, max_price, log_frequency_range):
    return np.interp(price, [min_price, max_price], [10**_ for _ in log_frequency_range])
```

```python
10**C2_log, 10**C3_log
```

```python
np.interp(2000, [0, 10000], [10**C2_log, 10**C3_log])
```

```python
# this should have returned the same as above
get_frequency(2000, 0, 10000, [C2_log, C2_log])
```

```python

```
