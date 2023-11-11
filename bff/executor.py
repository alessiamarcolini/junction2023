import uuid
import socketio
from threading import Thread


# standard Python


class Executor(Thread):
    def __init__(self, url, taskQueue):
        Thread.__init__(self)
        self.sio = socketio.SimpleClient()
        self.url = url
        self.execution = None
        self.taskQueue = taskQueue

    def run(self):
        self.sio.connect(self.url)

        while True:
            task = self.taskQueue.get()
            execution = task["execution"]
            user_sio = task["user_sio"]

            execution["status"] = "requested"
            self.sio.emit("execute", execution)
            user_sio.emit("execution_updated", execution)

            while True:
                event = self.sio.receive()
                event_type = event[0]

                if event_type == "finalize":
                    execution["status"] = "completed"
                    user_sio.emit("execution_updated", execution)
                    break
                elif event_type == "started":
                    execution["status"] = "started"
                    user_sio.emit("execution_updated", execution)
