from queue import Queue
from uuid import uuid4

from executor import Executor

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


def execute(sio, messages):
    execution_id = str(uuid4())
    execution = {
        "id": execution_id,
        "status": "scheduled",
        "messages": messages,
        "progress": -1,
    }
    task = {
        "execution": execution,
        "user_sio": sio,
    }
    taskQueue.put(task)

    sio.emit("execution_created", execution)


class DummyClient:
    def emit(self, *args):
        print(args)
        if args[0] == "execution_updated":
            if args[1]["status"] == "completed":
                exit(0)


execute(DummyClient(), ["hello", "world"])
