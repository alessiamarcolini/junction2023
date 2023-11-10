from model_handler import ModelHandler
from llama_cpp import Llama
import config as cfg


class LlamaModule:
    def __init__(self, modelName="llama-2-7B-chat"):
        self.modelPath = cfg.models[modelName]
        self.model = Llama(model_path=modelPath)
        self.modelHandler = ModelHandler()
        self.maxTokens = 256
        self.stopCharacters = ["\n"]
        self.stream = True

    def execute(self, handler: ModelHandler):
        prompt = handler.prompt()
        print(f"Prompt recieved {prompt}")

        handler.send_text("Hello world")
        handler.send_image("https://i.imgur.com/2X2IDEA.jpeg")
        handler.finalize()

        pass

    def generate_response(self, prompt):
        wordGenerator = self.model.create_completion(
            prompt,
            max_tokens=self.maxTokens,
            stop=self.stopCharacters,
            stream=self.stream
            )
        for word in wordGenerator:
            self.modelHandler.send_text(word)
        
        # TODO - remove
        self.modelHandler.finalize()
