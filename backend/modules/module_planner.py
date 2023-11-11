# Base packages
from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal
import logging

# Custom packages
from backend.model_handler.model_handler import ModelHandler
from backend.modules.module_base import ModuleBase
from backend.types.orchestration_types import OrchestrationStep
import backend.config as cfg

# 3-rd party packages
from llama_cpp import Llama

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

Input: """

MODEL_PROMPT = """
You are an assistant who needs to decide whether it 
makes sense to apply a set of pre-trained machine learning
models to the problem. These models are:

ENERGY PRICE FORECAST MODEL: Predicts energy prices up to
6 months into the future.

STEEL PRICE FORECAST MODEL: Predicts steel alloy prices
up to 6 months into the future.

List ALL models applicable SEPARATED BY COMMAS. If NO MODELS
ARE APPLICABLE, say "NONE". Here are some examples:

Input: I want to know the price of purchasing steel in 6 weeks' time. Can you help me?
Output: STEEL PRICE FORECAST MODEL

Input: Do you know how much energy it takes to produce steel?
Output: NONE

Input: I want to know the energy costs for manufacturing steel in 6 weeks' time.
Can you help me?
Output: ENERGY PRICE FORECAST MODEL

Input: I want to forecast the profit margin for producing steel for the next 2 months.
Can you help me come up with an estimate?
Output: ENERGY PRICE FORECAST MODEL, STEEL PRICE FORECAST MODEL

Input: I want to know the latest news about the steel industry. Can you summarize them
for me please?
Output: NONE

Input: """

BREAKDOWN_PROMPT = """
You are an assistant and your task is to break down tasks into
smaller bits. Your output should contain ONLY THE SUB-TASKS with 
each sub-task starting on a NEW LINE.

Here are some examples to help:


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

    def execute(self, handler: ModelHandler) -> List[OrchestrationStep]:
        logging.info("Executing planner function")
        self.__modelHandler = handler
        messages = handler.messages()

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")
        messages[-1]["content"] = FILTER_PROMPT + messages[-1]["content"] + "\n Output:"

        # Task 1 - do we need to answer this message?
        for i in range(maxRetries):
            # TODO: Remove - testing
            responseText = "accept"
            break
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=16,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content'].lower()
            logging.info(f"Filter response {i} generated: {responseText}")

            if responseText in ["accept", "decline"]:
                break
            
            logging.info(f"Invalid filtering response. Retrying ... ({i}/{self.__maxRetries})")
        
        # Decline - return plan
        if responseText == "decline":
            return [{
                "role": "summary",
                "name": "decline",
                "reason": "Input not related to steel industry"
            }]
        
        # Accept - create plan
        messages = handler.messages()
        logging.info(f"Deciding on models to use for prompt: {messages[-1]["content"]}")
        messages[-1]["content"] = MODEL_PROMPT + messages[-1]["content"] + "\n Output:"

        # Add custom prompt to message
        for i in range(maxRetries):
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=128,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content'].lower()
            logging.info(f"Filter response {i} generated: {responseText}")

            # Stop generating when correct classification is achieved
            acceptableResponses = ["forecast model", "none"]
            if any(word in responseText for word in acceptableResponses):
                break
        
        # Get models
        modelNames = ["energy price forecast model", "steel price forecast model"]
        models = [word in responseText for word in modelNames]

        # Break down problem

        # Create orchestration plan

        # Return orchestration plan