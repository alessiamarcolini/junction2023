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

    @sio.on("execute")
    def execute(sid, execution):
        print(execution)
        sio.emit("started", execution, room=sid)
        sio.emit("finalize", execution, room=sid)

    pass


def main():
    sio = socketio.Server()
    app = socketio.WSGIApp(sio, static_files=STATIC_FILES)
    routes(sio)

    if __name__ == "__main__":
        eventlet.wsgi.server(eventlet.listen(("", 5001)), app)


main()
