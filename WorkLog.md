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

# 2021-06-17 22:29:08.889910: clock-in

# 2021-06-17 21:59:46.147344: clock-out

* allowing date range to load on the fly
Check out ableton, midi

8 measures, 4/4 time, 
push the tempo.. 1440 beats per minute
3 hour candles? 8 beats

# 2021-06-17 21:34:12.651429: clock-in

# 2021-06-15 23:29:37.846516: clock-out

* saving historical data in daily files

# 2021-06-15 21:52:35.466441: clock-in

# 2021-06-14 23:36:15.632618: clock-out: T-45m 


# 2021-06-14 22:03:32.676556: clock-in

# 2021-06-13 23:38:42.855196: clock-out: T-10m 

* added sub range select

# 2021-06-13 22:32:12.627082: clock-in

# 2021-06-13 16:40:53.909382: clock-out

* testing start,end playback

# 2021-06-13 15:57:20.258581: clock-in

# 2021-06-13 13:11:47.189135: clock-out: T-10m 

* building in docker

# 2021-06-13 11:44:34.643876: clock-in

# 2021-06-12 23:44:04.566372: clock-out: T-10m 


# 2021-06-12 23:32:14.026151: clock-in

# 2021-06-12 23:15:40.277053: clock-out

* added rests toggle

# 2021-06-12 23:04:15.082670: clock-in

# 2021-06-12 14:00:50.574441: clock-out

* merge toggle

# 2021-06-12 12:50:03.490012: clock-in

# 2021-06-10 22:50:35.107916: clock-out

* merging by amplitude

# 2021-06-10 21:26:00.698998: clock-in

# 2021-06-10 21:25:20.990707: clock-out


# 2021-06-10 20:33:18.558354: clock-in

# 2021-06-10 01:05:01.630823: clock-out

* merged pitches, added rests, tone pitch dropdown

# 2021-06-09 22:56:32.687035: clock-in

# 2021-06-08 22:24:48.237340: clock-out

* added pitch range slider

# 2021-06-08 20:36:05.302294: clock-in

# 2021-05-31 12:01:32.717887: clock-out


# 2021-05-31 11:48:25.059119: clock-in

# 2021-05-31 11:24:43.444204: clock-out: T-13h 


# 2021-05-30 19:57:04.403863: clock-in

# 2021-05-30 19:30:13.440804: clock-out: T-1h 


# 2021-05-30 17:28:19.136269: clock-in

# 2021-05-30 02:33:40.434820: clock-out

* basic dash layout, test beeping, loading price history

# 2021-05-30 02:32:35.340810: clock-in: T-1h 

# 2021-05-29 23:18:41.414068: clock-out: T-1h 


# 2021-05-29 20:06:06.278965: clock-in

# 2021-05-29 19:54:28.225556: clock-out: T-3h 

* installing requirements


# 2021-05-29 15:49:10.496087: clock-in

