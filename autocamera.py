#!/usr/bin/env python3
# Copyright (c) 2015 Vibhav Pant <vibhavp@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from getpass import getpass
from websocket import create_connection
import requests
import json
import time
import datetime
import threading

###################################################################
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
                #lambda e: e["event_type"] == "TF2LineParser::Events::MedicDeath",

                # Uncomment to spectate ubersaw kills
                #lambda e: e["weapon"] == "ubersaw",
                lambda e: e["customkill"] == "backstab",
                lambda e: e["customkill"] == "headshot"]
###################################################################

# Stuff after this point shouldn't usually bother you if you're the
# cameraperson
global_lock = threading.Lock()
thread_exit = False

# an event is a tuple of the form (player, time).
# player is a string containing the name of the player we want to spectate
# time is the timestamp (in seconds) of when the event will take place
event_queue = []


def event_push(event):
    ts = event["created_at"]
    ts = datetime.datetime(int(ts[:4]), int(ts[5:7]), int(ts[8:10]),
                           int(ts[11:13]), int(ts[14:16]), int(ts[17:19]))
    ts = int(ts.timestamp())
    # Only push if the event didn't occur within 5 seconds of the last
    # event
    if (event_queue == [] or ts - event_queue[0][1] > 5):
        # The event occurs at current_time + 90 (assumed STV delay)
        event_queue.insert(0, (event[spec_player], ts + 90))


def record_demo(wsocket, player, time, event_type):
    ts = datetime.datetime.fromtimestamp(time)
    time.sleep(time - record_start)
    request = "{\"type\": \"command\", \"command\":\"record %s_%s_%s:%s:%s\"}" \
              % (player, event_type, ts.hour, ts.minute, ts.second)
    wsocket.send(request)
    time.sleep(int(time.time()) - time + record_stop)
    wsocket.send("{\"type\": \"command\", \"comamnd\":\"stop\"}")


def event_type(event):
    if event["event_type"][len(event)-1] == 't':  # airshot
        return "airshot"

    if event["event_type"][len(event)-1] == 'h':  # medic death
        return "med_drop"

    return event["customkill"]


def send_events(wsocket):
    while True:
        # Wait until the event queue isn't empty
        while (event_queue == []):
            if thread_exit:
                exit(1)
            time.sleep(1)

        global_lock.acquire(True)
        event = event_queue.pop()
        global_lock.release()

        player, time = event[0], event[1]

        # Sleep for (time_when_event_happens_on_stv - current_time - spec_on)
        time.sleep(time - int(time.time()) - spec_on)

        # Send request to ExternalExtensions to execute the command
        # spec_player <player>
        request = "{ \"type\": \"command\", \"comand\": \"spec_player %s\"}" \
                  % player
        wsocket.send(request)
        if record:
            t = threading.Thread(target=record_demo, args=(wsocket, player,
                                                           time,
                                                           event_type(event)))
            t.start()


def add_events(js, index):
    """Loop through events in js (from index) and push the important ones to
    the event queue. Returns the last relevent event"""
    last_event = None
    for event in js[index:]:
        for event_check in event_checks:
            if event_check(event):
                last_event = event
                global_lock.acquire(True)
                event_push(event)
                global_lock.release()
    return last_event


def main():

    global thread_exit
    global url

    print("Enter Match ID")
    url = url % input()

    print("Enter feed username")
    uname = input()

    print("Enter feed password")
    pwd = getpass.getpass()

    # Connect to ExternalExtensions' websocket
    print("Connecting to ExternalExtensions...",)
    try:
        ws = create_connection("ws://127.0.0.1:%s" % websockets_port)
    except ConnectionRefusedError:
        print("Connection to ExternalExtensions refused.")
    finally:
        print("Connection failed. Exiting")
        exit(1)

    print("Connected.")

    t = threading.Thread(target=send_events, args=ws)
    t.start()

    last_event = None
    while True:
        req = requests.get(url, auth=(uname, pwd))
        if req.status_code == 401:
            print("Wrong Username and/or password")
            thread_exit = True
            exit(1)
        js = json.load(req.text)
        if last_event is None:
            last_event = add_events(js, 0)
        else:
            last_event = add_events(js, js.index(last_event) + 1)


if __name__ == "__main__":
    main()
