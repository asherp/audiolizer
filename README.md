
# About

Market audiolization dashboard

![Market audiolizer screenshot](https://github.com/asherp/audiolizer/raw/master/audiolizer0.2_screen_shot.png)

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

# Running from Docker

Running without temp directories:
```console
docker run -p 8051:8051 -it apembroke/audiolizer
```

Running with mounted temp directories:

```console
docker run -v /tmp/audio_files:/home/audiolizer/audiolizer/assets -v /tmp/price_data:/home/audiolizer/audiolizer/history -p 8051:8051 -it apembroke/audiolizer
```