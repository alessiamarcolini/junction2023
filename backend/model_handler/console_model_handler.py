from .model_handler import ModelHandler


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

    def messages(self) -> List[str]:
        if self.__messages is None:
            self.__messages = [input("Enter prompt: ")]
        print(self.__messages)
        return self.__messages

    def update_status_message(self, status: str) -> None:
        print(status_message)
        pass

    def update_progress_bar(self, progress: Union[int, None]) -> None:
        print(progres_percent)
        pass