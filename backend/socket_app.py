from queue import Queue

import eventlet
import socketio

sio = socketio.Client()
sio.connect("http://localhost:5001")


@sio.event
def execute(data):
    print("execution requested")

sio.wait()

