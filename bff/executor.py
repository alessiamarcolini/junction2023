import eventlet

# standard Python


class Executor:
    def __init__(self, sio, taskQueue):
        self.executor_sio = sio
        self.taskQueue = taskQueue
        self.execution = None
        self.user_sio = None
        self.__stopped = False

    def run(self):
        while True:
            if self.__stopped:
                print(f"Executor({self.executor_sio.sid}) Stopped")
                break

            task = None
            try:
                print(f"Executor({self.executor_sio.sid}) Polling task")
                task = self.taskQueue.get(timeout=3)
            except:
                continue

            print(f"Executor({self.executor_sio.sid}) Got task {task}")

            self.execution = task["execution"]
            self.user_sio = task["user_sio"]

            self.execution["status"] = "sceduled"
            self.executor_sio.emit("execute", self.execution)
            self.user_sio.emit("execution_updated", self.execution)

            while True:
                print(
                    f"Executor({self.executor_sio.sid}) Waiting for execution to finish"
                )
                eventlet.sleep(3)
                if not self.execution or self.__stopped:
                    break

    def start(self):
        eventlet.spawn(self.run)

    def recieve(self, event, *data):
        print(f"Executor({self.executor_sio.sid}) Event {event} recieved {data}")
        if event == "finalize":
            print(f"Executor({self.executor_sio.sid}) Finalizing execution")
            self.execution["status"] = "completed"
            self.execution["progress"] = None
            self.user_sio.emit("execution_updated", self.execution)
            self.user_sio.emit("finalize", self.execution)
            self.user_sio = None
            self.execution = None
        elif event == "send_text":
            self.user_sio.emit(
                "text_recieved", {"id": self.execution["id"], "text": data[0]}
            )
        elif event == "send_image":
            print(f"Executor({self.executor_sio.sid}) Recieved image {data[0]}")
        elif event == "update_status_message":
            self.execution["status"] = data[0] if len(data) > 0 else None
            self.user_sio.emit("execution_updated", self.execution)
        elif event == "update_status_progress":
            self.execution["progress"] = data[0] if len(data) > 0 else None
            self.user_sio.emit("execution_updated", self.execution)

    def stop(self):
        self.__stopped = True
        self.execution = None
        self.user_sio = None
