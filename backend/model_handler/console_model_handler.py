from .model_handler import ModelHandler


class ConsoleModelHandler(ModelHandler):
    def __init__(self):
        super().__init__()
        self.__prompt = None
        self.__finalized = False
        self.__quiet = False

    def send_text(self, text):
        if not self.__quiet:
            print(text)

    def prompt(self):
        if self.__prompt is None:
            self.__prompt = input("Enter prompt: ")
        return self.__prompt

    def send_image(self, image):
        print(f"Image recieved {image}")

    def finalize(self):
        self.__finalized = True
        if not self.__quiet:
            print("Final output sent")
