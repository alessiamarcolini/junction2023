from backend.model_handler.model_handler import ModelHandler
from backend.modules.module_base import ModuleBase
from llama_cpp import Llama
import backend.config as cfg
import logging

from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

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

Input:
"""


class PlannerModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B"):
        super().__init__()
        self.__model = Llama(model_path=cfg.models[modelName], n_gpu_layers=28)
        self.modelName = modelName
        self.maxOutputTokens = 1024
        self.stream = False
        self.temperature = 0.95
        self.response_format = "json_object"

        logging.info(f"Initialized planner model {modelName}")

    def execute(self, handler: ModelHandler):
        logging.info("Executing planner function")
        self.__modelHandler = handler
        messages = handler.messages()

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")
        messages[-1]["content"] = CUSTOM_PROMPT + messages[-1]["content"] + "\n Output:"

        # Get latest prompt + respond
        response = self.__model.create_chat_completion(
            messages,
            max_tokens=self.maxOutputTokens,
            stream=self.stream,
            temperature=self.temperature,
            #response_format=self.response_format
        )
        logging.info(f"Response generated: {response['choices'][0]['message']['content']}")
        
        # TODO - remove
        self.__modelHandler.finalize()