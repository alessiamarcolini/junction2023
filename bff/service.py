import eventlet
import socketio
from queue import Queue
from .executor import Executor

STATIC_FILES = {
    "/": "../frontend/build/index.html",
    "/static": "../frontend/build/static",
}

taskQueue = Queue()

executors = [
  Executor("http://localhost:5001", taskQueue),
]

for executor in executors:
    executor.start()


def routes(sio):
    @sio.on("connect")
    def connect(sid, environ):
        print("connect ", sid)

    def execute(sid, messages):
        print("execute ", sid, execution)

    pass


def main():
    sio = socketio.Server()
    app = socketio.WSGIApp(sio, static_files=STATIC_FILES)
    routes(sio)

    if __name__ == "__main__":
        eventlet.wsgi.server(eventlet.listen(("", 5000)), app)


main()
