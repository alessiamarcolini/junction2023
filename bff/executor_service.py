from queue import Queue

import socketio
from executor import Executor


STATIC_FILES = {
    "/": "../frontend/build/index.html",
    "/static": "../frontend/build/static",
}

taskQueue = Queue()

executors = {}


def routes(sio):
    @sio.on("connect")
    def connect(sid, environ):
        print(f"Connecting executor {sid}")
        executor = Executor(sid, sio, taskQueue)
        executor.start()

    @sio.on("disconnect")
    def disconnect(sid):
        print(f"Disconnecting executor {sid}")
        executor = executors[sid]
        if not executor:
            print(
                f"unable to handle disconnection, because there is no registered executor for it {sid}"
            )
            return
        executor.stop()
        executors[sid] = None

    @sio.on("*")
    def handle_messages(event, sid, data):
        executor = executors[sid]
        if not executor:
            print(
                f"unable to handle message, because there is no registered executor for it {event} {data}"
            )
            return
        executor.revieve(event, data)


sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files=STATIC_FILES)
routes(sio)
