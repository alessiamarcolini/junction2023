from model_handler import ModelHandler


class LlamaModule:
    def execute(self, handler: ModelHandler):
        prompt = handler.prompt()
        print(f"Prompt recieved {prompt}")

        handler.send_text("Hello world")
        handler.send_image("https://i.imgur.com/2X2IDEA.jpeg")
        handler.finalize()

        pass
