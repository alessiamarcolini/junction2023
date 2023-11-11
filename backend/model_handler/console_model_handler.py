from backend.model_handler.model_handler import ModelHandler
from backend.types.message_types import ChatCompletionRequestMessage, ChatCompletionRequestUserMessage

from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

class ConsoleModelHandler(ModelHandler):
    def __init__(self):
        super().__init__()
        self.__messages = None
        self.__finalized = False

    def send_text(self, text):
        print(text)

    def send_image(self, image):
        print(f"Image recieved {image}")

    def finalize(self):
        self.__finalized = True
        print("Final output sent")

    def messages(self) -> List[ChatCompletionRequestMessage]:
        if self.__messages is None:
            logging.info("No messages found! Asking for message...")
            self.__messages : List[ChatCompletionRequestUserMessage] = [{
                "role":"user",
                "content":input("Please type an input prompt: ")
            }]
        logging.info(f"Current messages: {self.__messages}")
        return self.__messages

    def update_status_message(self, status: str) -> None:
        print(status_message)
        pass

    def update_progress_bar(self, progress: Union[int, None]) -> None:
        print(progres_percent)
        pass

    def send_debug_thoughts(self, thought: str) -> None:
        print(thought)
        pass