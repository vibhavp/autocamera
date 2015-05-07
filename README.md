AutoCamera
=========

AutoCamera checks [Arie's live TF2 feed](https://github.com/Arie/tf2_live_stats) for big plays
, and changes the spectator cam accordingly. It is supposed to sit on
a secondary camera, and is meant to help view
**multiple perspectives** of in-game events. The secondary camera then can be viewed
on a split-screen. **Primary Camerawork is still supposed to be done by humans, and
in no way is AutoCamera a substitute for that**

For your frag video/instant replay needs, AutoCamera can also automate demos recordings,
with the relevant config. Demos can start and stop recording at a set time, and are
saved with the format `player_<event_type>_hour_minutes_seconds`.

Usage
----
Execute the script with `python autocamera.py`

Enter the Match ID as per the live feed, the user name, and password to the live feed.

AutoCamera will start listening for events, and spectate and/or record them on the local
TF2 process as necessary.

Configuration
------------
The config variables are stored in `autocamera.py`. A little bit of Python knowledge is required
if you want to define your own custom events. Here's what the default config is:

~~~python
# The port on which autocamera.py will listen
feed_port = "5555"
# The port on which ExternelExtensions will listen
websockets_port = "2006"
# The cheat feed delay, in seconds
feed_delay = 70
# Spectate player when these much seconds are left
spec_on = 5
# Set to True if you want to record a demo of the play
record = False
# Seconds before the play the demo will start recording from
record_start = 5
# Seconds after which the demo will stop recording
record_stop = 5
# The player you want to spectate. Can be either of "player_name"
# or "target_name"
spec_player = "player_name"
# URL to the cheat feed's JSON endpoint
url = "http://live.fakkelbrigade.eu/pages/streamer_stats.json?match_id="
# Events to spectate
event_checks = [lambda e: e["event_type"] == "TF2LineParser::Events::Airshot",
                # Uncomment to spectate medic deaths
                # lambda e: e["event_type"] == "TF2LineParser::Events::MedicDeath",
                # Uncomment to spectate ubersaw kills
                # lambda e: e["weapon"] == "ubersaw",
                lambda e: e["customkill"] == "backstab",
                lambda e: e["customkill"] == "headshot"]
~~~

Requirements
------------

* Python 3
* [ExternalExtensions](https://github.com/fwdcp/ExternalExtensions)
* [websockets-client](https://github.com/liris/websocket-client)
* [Arie's live TF2 feed](https://github.com/Arie/tf2_live_stats)

Thanks
------
**thesupremecommander** - for writing ExternalExtensions

**Arie** - for writing [live TF2 feed](https://github.com/Arie/tf2_live_stats)

**dashner, davidthewin** - for information on TF2 Camerawork.
