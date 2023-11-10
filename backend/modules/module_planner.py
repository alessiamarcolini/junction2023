from model_handler import ModelHandler
from .module_base import ModuleBase
from llama_cpp import Llama
import config as cfg

CUSTOM_PROMPT = """
You are a trustworthy assistant breaking down complex problems
into easy-to-solve chunks. You have the following trusted models
at your disposal:

energy_price_forecast model:
- parameters: 
    - months: float

steel_price_forecast model:
- parameters: 
    - months: float
    - alloy: string

Please use the above models to break down the problem given at 
the end. Please respond in json format with the model name and
model parameters and include your reasoning. If these models cannot
solve the problem, please say "I cannot solve the problem".

Here is one example to help:
Input: What is the expected development of stainless steel 
market pricing for 10B general steel alloy in two weeks?
Output:
[
    {"modelName": "steel_price_forecast",
    "parameters": {
        "months": 0.5,
        "alloy": "10B general steel"
        }
    }
]

Output:
"""


class PlannerModule(ModuleBase):
    def __init__(self, 
        modelName: str ="llama-2-7B-chat"):
        super().__init__()
        self.__model = Llama(model_path=cfg.models[modelName])
        self.modelName = modelName
        self.maxOutputTokens = 2048
        self.stream = False
        self.temperature = 0.1
        self.response_format = "json_object"

    def execute(self, handler: ModelHandler):
        self.__modelHandler = handler
        messages = handler.messages()

        # Add custom prompt to beginning of
        # last message
        messages[-1] = CUSTOM_PROMPT + messages[-1]

        # Get latest prompt + respond
        response = self.__model.create_chat_completion(
            messages,
            max_tokens=self.maxOutputTokens,
            stream=self.stream,
            temperature=self.temperature,
            response_format=self.response_format
        )

        # Try to make sense of the response
        a = 1
        
        # TODO - remove
        self.__modelHandler.finalize()

if __name__ == "__main__":
    PlannerModule().execute("""I want to help my friend generate pictures of cats using AI.
        Can you suggest some python code to achieve this?""")