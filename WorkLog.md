* pushing apembroke/audiolizer:0.2
* fixed bug in import
* sample midi

### 2021-06-21 23:57:58.681256: clock-in

* adding sample midi
### 2021-06-21 23:36:47.974003: clock-out

* added favicon
* moving into assets
* icon courtesy of SiLVa
* adding screen shot
* ignoring wav and midi
* added cache setting
* filling data gaps
* irig 2 setup

### 2021-06-21 20:06:43.967497: clock-in

### 2021-06-21 18:52:53.877091: clock-out

* fixing data gaps

### 2021-06-21 17:59:56.336985: clock-in

### 2021-06-20 16:03:45.241495: clock-out

* meeting with Randy

1. add floor function to normalize frequencies - accomplished through pitch conversion
1. slider that controls modulus on frequency [1, 100] so melody can cycle
1. 3 market displays - monthly, weekly, daily - put into a dial - multiple rows
1. umbrel as a distribution mechanism - be a good citizen w.r.t. disk space
1. estimate footprint of settings (size of files generated)
1. icon and screen shots
1. umbrel uses tor - is that a problem for coinbase price api? Consider privacy - Can this expose user's ip address?
1. scales - ease of use toggle between cmajor and aminor work well together
1. how to achieve harmony and melody is in the relationship between major and minor scales
1. market data would be like trebble clef (middle c and above) and another market feed as the bass clef (middle c and below) - lower case c is middle c - automated sheet music will help alot
1. weekly candles could be base cleff. hourly could be trebble
1. allow open/high/low/close selection - this is the same in music
1. audiolizer sounds great on the phone!
1. btc ledger as data source? umbrel platform gives access to all kinds of btc data...

required reading
On the Sensations of Tone - Helmholtz
The Study of Counterpoint: From Johann Joseph Fux's Gradus Ad Parnassum

### 2021-06-20 14:39:47.114093: clock-in

### 2021-06-20 00:38:28.710038: clock-out

* pushing docker version
* looking at html midi players:
* https://github.com/cifkao/html-midi-player javascript - but how to embed?
* https://surikov.github.io/webaudiofont/ this is a really beautiful html-only midi system. we could build a dash component around this. That would open the door to custom instruments, etc.

* added midi download

### 2021-06-19 21:56:47.016441: clock-in

### 2021-06-19 20:14:25.744423: clock-out

* changed src to github raw

### 2021-06-19 20:13:50.087569: clock-in: T-4m 

### 2021-06-19 20:08:24.558530: clock-out

* a better sample illustrating duration

### 2021-06-19 19:37:22.200467: clock-in

### 2021-06-19 00:43:59.135736: clock-out

* added code highlighting
* sample audio
* fixed site name

### 2021-06-19 00:43:16.152887: clock-in: T-14m 

### 2021-06-19 00:28:38.532399: clock-out

* added worklog

### 2021-06-19 00:05:44.387679: clock-in

### 2021-06-19 00:02:40.078861: clock-out

* documentation improvements

### 2021-06-18 22:10:09.398018: clock-in

### 2021-06-18 21:07:39.810058: clock-out

* adding docs
* removed legend, added docs

### 2021-06-18 18:47:04.388103: clock-in

* you can calculate the % data loaded by comparing list of missing files to those present

### 2021-06-18 00:25:05.504006: clock-out

* updating instructions
* running from audiolizer subdir

Running without temp directories:
```console
docker run -p 8051:8051 -it apembroke/audiolizer

```

Running from temp directories:

```console
docker run -v /tmp/audio_files:/home/audiolizer/audiolizer/assets -v /tmp/price_data:/home/audiolizer/audiolizer/history -p 8051:8051 -it apembroke/audiolizer
```
* setting environment variable
* moving install paths
* creating cache directories
* building docker image
* building docker image from clean git repo

```console
git archive --format=tar --prefix=audiolizer/ HEAD | (cd /tmp && tar xf -)
docker build -t apembroke/audiolizer -f /tmp/audiolizer/Dockerfile /tmp/audiolizer
```
* adding midi
* tempo in yaml
* added tempo
* midi example

```python
from midiutil import MIDIFile

degrees  = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number
track    = 0
channel  = 0
time     = 0    # In beats
duration = 1    # In beats
tempo    = 60   # In BPM
volume   = 100  # 0-127, as per the MIDI standard

MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                      # automatically)
MyMIDI.addTempo(track, time, tempo)

for i, pitch in enumerate(degrees):
    MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

with open("major-scale.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
```

### 2021-06-17 22:29:08.889910: clock-in

### 2021-06-17 21:59:46.147344: clock-out

* allowing date range to load on the fly
Check out ableton, midi

8 measures, 4/4 time, 
push the tempo.. 1440 beats per minute
3 hour candles? 8 beats

### 2021-06-17 21:34:12.651429: clock-in

### 2021-06-15 23:29:37.846516: clock-out

* saving historical data in daily files

### 2021-06-15 21:52:35.466441: clock-in

### 2021-06-14 23:36:15.632618: clock-out: T-45m 


### 2021-06-14 22:03:32.676556: clock-in

### 2021-06-13 23:38:42.855196: clock-out: T-10m 

* added sub range select

### 2021-06-13 22:32:12.627082: clock-in

### 2021-06-13 16:40:53.909382: clock-out

* testing start,end playback

### 2021-06-13 15:57:20.258581: clock-in

### 2021-06-13 13:11:47.189135: clock-out: T-10m 

* building in docker

### 2021-06-13 11:44:34.643876: clock-in

### 2021-06-12 23:44:04.566372: clock-out: T-10m 


### 2021-06-12 23:32:14.026151: clock-in

### 2021-06-12 23:15:40.277053: clock-out

* added rests toggle

### 2021-06-12 23:04:15.082670: clock-in

### 2021-06-12 14:00:50.574441: clock-out

* merge toggle

### 2021-06-12 12:50:03.490012: clock-in

### 2021-06-10 22:50:35.107916: clock-out

* merging by amplitude

### 2021-06-10 21:26:00.698998: clock-in

### 2021-06-10 21:25:20.990707: clock-out


### 2021-06-10 20:33:18.558354: clock-in

### 2021-06-10 01:05:01.630823: clock-out

* merged pitches, added rests, tone pitch dropdown

### 2021-06-09 22:56:32.687035: clock-in

### 2021-06-08 22:24:48.237340: clock-out

* added pitch range slider

### 2021-06-08 20:36:05.302294: clock-in

### 2021-05-31 12:01:32.717887: clock-out


### 2021-05-31 11:48:25.059119: clock-in

### 2021-05-31 11:24:43.444204: clock-out: T-13h 


### 2021-05-30 19:57:04.403863: clock-in

### 2021-05-30 19:30:13.440804: clock-out: T-1h 


### 2021-05-30 17:28:19.136269: clock-in

### 2021-05-30 02:33:40.434820: clock-out

* basic dash layout, test beeping, loading price history

### 2021-05-30 02:32:35.340810: clock-in: T-1h 

### 2021-05-29 23:18:41.414068: clock-out: T-1h 


### 2021-05-29 20:06:06.278965: clock-in

### 2021-05-29 19:54:28.225556: clock-out: T-3h 

* installing requirements


### 2021-05-29 15:49:10.496087: clock-in

