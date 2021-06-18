
# About

Market audiolization dashboard


## Requirements

* numpy
* pandas
* plotly
* Historic-Crypto (pip)
* pyaudio (conda)
* audiogen (pip)

# Running from Docker

Running without temp directories:
```console
docker run -p 8051:8051 -it apembroke/audiolizer
```

Running with mounted temp directories:

```console
docker run -v /tmp/audio_files:/home/audiolizer/audiolizer/assets -v /tmp/price_data:/home/audiolizer/audiolizer/history -p 8051:8051 -it apembroke/audiolizer
```