from model_handler import ModelHandler
from .module_base import ModuleBase
from llama_cpp import Llama
import config as cfg


class PlannerModule(ModuleBase):
    def __init__(self, 
        modelName: str ="llama-2-7B-chat"):
        super().__init__()
        self.__model = Llama(model_path=cfg.models[modelName])
        self.modelName = modelName
        self.maxOutputTokens = 2048
        self.stream = False

    def execute(self, handler: ModelHandler):
        self.__modelHandler = handler
        messages = handler.messages()


        handler.send_text("Hello world")
        handler.send_image("https://i.imgur.com/2X2IDEA.jpeg")
        handler.finalize()

        pass

    def generate_response(self):
        wordGenerator = self.__model.create_chat_completion(
            self.__modelHandler.messages(),
            max_tokens=self.maxOutputTokens,
            stop=self.stopCharacters,
            stream=self.stream
            )
        for word in wordGenerator:
            self.__modelHandler.send_text(word["choices"][0]["text"])
        
        # TODO - remove
        self.__modelHandler.finalize()

if __name__ == "__main__":
    LlamaModule().generate_response("I want to help my friend generate pictures of cats using AI. Can you suggest some python code to achieve this?")