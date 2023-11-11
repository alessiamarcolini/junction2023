import uuid
from typing import Any, List, Union

from .model_handler import ModelHandler


class SocketModelHandler(ModelHandler):
    def __init__(self, execuiton, sio):
        super().__init__()
        self.__execution = execuiton
        self.__sio = sio

    def send_text(self, text):
        print(f"Sending text {text}")
        self.__sio.emit("send_text", text)

    def send_asset(self, type: str, asset: Any):
        id = str(uuid.uuid4())
        filename = f"{id}.{type}"
        print(f"Sending {filename} {asset}")
        self.__sio.emit("send_asset", {"id": id, "type": type, "asset": asset})

    def finalize(self):
        print(f"Finalizing")
        self.__sio.emit("finalize")

    def messages(self) -> List[str]:
        return self.__execution["request"]

    def update_status_message(self, status: str) -> None:
        print(f"Updating status message {status}")
        self.__sio.emit("update_status_message", status)

    def update_progress_bar(self, progress: Union[int, None]) -> None:
        print(f"Updating status progress {progress}")
        self.__sio.emit("update_status_progress", progress)

    def send_debug_thoughts(self, thought: str) -> None:
        self.__sio.emit("send_debug_thought", thought)
        pass
