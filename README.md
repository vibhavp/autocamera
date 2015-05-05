AutoCamera
=========

[teamfortress.tv thread](http://teamfortress.tv/thread/24943/autocamera#426067)

AutoCamera listens to players on a TCP connection, and changes the spectator cam
accordingly. It is supposed to sit on a secondary camera, and is meant to help view
**multiple perspectives** of in-game events. **Primary Camerawork is still supposed to
be done by humans, and in no way is AutoCamera a substitute for that** The secondary
camera then can be viewed on a split-screen.

Requirements
------------

* Python 3
* [ExternalExtensions](https://github.com/fwdcp/ExternalExtensions)
* [websockets-client](https://github.com/liris/websocket-client)
* [ZeroMQ/pymq](http://zeromq.org/bindings:python)
* [Arie's live TF2 feed](https://github.com/Arie/tf2_live_stats)

Thanks
------
**thesupremecommander** - for writing ExternalExtensions

**Alex "dashner" Pylyshyn, David "davidthewin" Green** - for information on TF2 Camerawork.
