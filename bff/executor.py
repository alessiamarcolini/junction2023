import time
from threading import Thread

# standard Python


class Executor(Thread):
    def __init__(self, sid, sio, taskQueue):
        Thread.__init__(self)
        self.sio = sio
        self.sid = sid
        self.taskQueue = taskQueue
        self.execution = None
        self.user_sio = None

    def run(self):
        while True:
            print(f"Executor({self.sid}) Getting new task")
            task = self.taskQueue.get()
            print(f"Executor({self.sid}) Got task {task}")

            self.execution = task["execution"]
            self.user_sio = task["user_sio"]

            self.execution["status"] = "requested"
            self.sio.emit("execute", self.execution)
            self.user_sio.emit("execution_updated", self.execution)

            while True:
                print(f"Executor({self.sid}) Waiting for execution to finish")
                time.sleep(3)
                if not self.execution:
                    break

    def recieve(self, event, data):
        print(f"Executor({self.sid}) Event {event} recieved {data}")
