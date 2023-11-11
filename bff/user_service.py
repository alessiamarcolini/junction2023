from queue import Queue

import eventlet
import socketio

STATIC_FILES = {
    "/": "../frontend/build/index.html",
    "/static": "../frontend/build/static",
}


def routes(sio):
    @sio.on("connect")
    def connect(sid, environ):
        print("connect ", sid)

    def execute(sid, messages):
        print("execute ")

    pass


sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files=STATIC_FILES)
routes(sio)
