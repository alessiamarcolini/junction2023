from queue import Queue

import socketio
from executor_service import request_execution
from socket_wrapper import SocketWrapper

STATIC_FILES = {
    "/": "../frontend/build/index.html",
    "/static": "../frontend/build/static",
}


def routes(sio):
    @sio.on("connect")
    def connect(sid, environ):
        print(f"User {sid} connected")

    @sio.event
    def execute(sid, messages):
        print(f"User requested execution {messages} ")
        user_sio = SocketWrapper(sio, sid)
        request_execution(messages, user_sio)

    pass


sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio, static_files=STATIC_FILES)

routes(sio)
