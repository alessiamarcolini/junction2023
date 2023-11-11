from backend.model_handler.model_handler import ModelHandler
from backend.modules.module_base import ModuleBase
from llama_cpp import Llama
import backend.config as cfg
import logging

from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

FILTER_PROMPT = """
You are an assistant filtering inputs for further processing.
IF THE PROBLEM IS RELATED TO THE STEEL INDUSTRY in any way,
you need to pass on the output for further processing. In these cases,
only generate one word: "PASS". Otherwise, you need to return the
word "DECLINE" for the request. RETURN ONLY ONE WORD.

Here are some examples:

Input: Can you generate some images of cats?
Output: DECLINE

Input: I want to know the price of steel in 3 months.
Output: PASS

Input: How much energy does steel processing consume? Can you forecast
factors influencing energy prices in the near future?
Output: PASS

Input: Can you help me generate some python code to print to the
console?
Output: DECLINE

Input: 
"""

BREAK_DOWN_PROMPT = """
You are an assistant breaking down complex problems into easy-to-solve chunks.
"""

MODEL_PROMPT = """
You have the following trusted models
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
"""


class PlannerModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B-instruct",
        maxRetries: int = 3):
        super().__init__()
        self.__model = Llama(model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=1024)
        self.__maxRetries = maxRetries
        self.modelName = modelName
        self.stream = False
        self.temperature = 0.95

        logging.info(f"Initialized planner model {modelName}")

    def execute(self, handler: ModelHandler):
        logging.info("Executing planner function")
        self.__modelHandler = handler
        messages = handler.messages()

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")
        messages[-1]["content"] = FILTER_PROMPT + messages[-1]["content"] + "\n Output:"

        # Task 1 - do we need to answer this message?
        for i in range(maxRetries):
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=16,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            logging.info(f"Filter response {i} generated: {responseText}")

            if responseText.lower() in ["accept", "decline"]:
                break
            
            logging.info(f"Invalid filtering response. Retrying ... ({i}/{self.__maxRetries})")
        
        # Decline - return plan
        
        
        # TODO - remove
        self.__modelHandler.finalize()