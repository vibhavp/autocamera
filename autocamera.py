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

#!/usr/bin/env python3
import zmq
from websocket import create_connection
import time
import threading
import pyautogui

###################################################################
# The port on which autocamera.py will listen
feed_port = "5555"
# The port on which ExternelExtensions with listen
websockets_port  = "2006"
# The STV delay, in seconds     
stv_delay = 90
# Spectate player when these much seconds are left
spec_on = 5
# bind configured in TF2 to autocamera_spec_player
camera_bind = 'k'
###################################################################

# Stuff after this point shouldn't usually bother you if you're the
# cameraperson
global_lock = threading.Lock()
thread_exit = False;

# an event is a tuple of the form (player, time).
# player is a string containing the name of the player we want to spectate
# time is the timestamp (in seconds) of when the event will take place
event_queue = []


def event_push(player):
    # Only push if the event didn't occur within 5 seconds of the last
    # event
    if (event_queue == [] or int(time.time()) - event_queue[0][1] > 5):
        # The event occurs at current_time + stv_delay
        event_queue.insert(0, (player, int(time.time() + stv_delay)))

def send_events():
    # Connect to ExternalExtensions' websocket
    print("Connecting to ExternalExtensions...")
    ws = create_connection("ws://127.0.0.1:%s" % websockets_port)
    print("Done.")
    
    while True:
        # Wait until the event queue isn't empty
        while (event_queue == []):
            if thread_exit:
                exit(0)
            time.sleep(1)

        global_lock.acquire(True)
        head_time = event_queue[len(event_queue) - 1][1]
        global_lock.release()

        # Sleep for (time_when_event_happens - current_time + spec_on) seconds
        time.sleep(head_time + spec_on)

        # Get the player to spec
        global_lock.acquire(True)
        head_player = event_queue.pop()
        global_lock.release()
        # Send request to ExternalExtensions to execute the command
        # spec_player <player>
        request = "{ \"type\": \"command\", \"comand\": \"spec_player %s\"}" % head_player
        ws.send(request)

def main():
    
    feed_context = zmq.Context()
    feed_socket = feed_context.socket(zmq.PAIR)
    feed_socket.bind("tcp://*:%s" % feed_port)

    t = threading.Thread(target=send_events)
    t.start()

    while True:
        # Get name of player to observe
        name = feed_socket.recv().decode("utf-8")
        if name == "exit":
            global thread_exit
            thread_exit = True
            feed_socket.disconnect("tcp://*:%s" % feed_port)
            exit(0)

        global_lock.acquire(True)
        event_push(name)
        global_lock.release()

if __name__ == "__main__":
    main()
