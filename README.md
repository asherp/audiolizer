
# About

Market audiolization dashboard

![Market audiolizer screenshot](https://github.com/asherp/audiolizer/raw/master/audiolizer0.2_screen_shot.png)

Here is the [midi file](https://github.com/asherp/audiolizer/raw/master/docs/assets/BTC_2020-09-01_2021-06-21_1W_C3_C5_pitch_25_75_240bpm_merged_rests.midi) for the above plot.

Visit the documenation site to learn [how it works](https://asherp.github.io/audiolizer/About/)!

## Requirements

* numpy
* pandas
* plotly
* Historic-Crypto (pip)
* pyaudio (conda)
* audiogen (pip)

docs dependences (optional)
* mkdocs (pip)
* tabulate (pip)

# Running from python

```console
git clone https://github.com/asherp/audiolizer
cd audiolizer
python audiolizer.py
```

You should see something like the following output
```
audiolizer temp data: ./history/
Dash is running on http://0.0.0.0:8051/

 * Serving Flask app 'audiolizer' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on

```
Open your browser to localhost:8051.

You may hear a startup sound when the application starts. If you don't, that's ok - the dashboard will still play through the browser! 

# Running from Docker

From the base of this repo, create a `.env` file and define the following variables

```bash
AUDIOLIZER_ASSETS=/full/path/to/temporary/audio_files
AUDIOLIZER_PRICES=/full/path/to/temporary/price_data
AUDIOLIZER_SRC=/full/path/to/audiolizer/repo
JUPYTER_PASSWORD=
```

Now run the audiolizer application:

```console
docker-compose up audiolizer
```
Open your browser to `localhost:80`

Running without temp directories:
```console
docker run -p 8051:8051 -it apembroke/audiolizer
```

Running with mounted temp directories:

```console
docker run -v /tmp/audio_files:/home/audiolizer/audiolizer/assets -v /tmp/price_data:/home/audiolizer/audiolizer/history -p 8051:8051 -it apembroke/audiolizer
```

