# Base packages
import logging
from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

# Own packages
from backend.model_handler.model_handler import ModelHandler
from backend.modules.module_base import ModuleBase
import backend.config as cfg

# 3rd party packages
from llama_cpp import Llama
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

CUSTOM_PROMPT = """ <s>[INST]
You are a trustworthy assistant breaking down complex problems
into easy-to-solve chunks. You have the following trusted models
at your disposal:

energy_price_forecast model:
- parameters: 
    - months (float): Number of months in future for prediction

steel_price_forecast model:
- parameters: 
    - months (float): Number of months in future for prediction
    - alloy (string): Steel alloy name

Please use the above models to break down the problem given at 
the end. Please respond in JSON FORMAT with the model name and
model parameters and include your reasoning. If these models cannot
solve the problem, please say "I cannot solve the problem".
[/INST]

Here is one example to help:
Input: What is the expected development of stainless steel 
market pricing for 10B general steel alloy in two weeks?
Output:
[{"modelName": "steel_price_forecast",
    "parameters": {
        "months": 0.5,
        "alloy": "10B general steel"}
}]
</s>

Input: {question}
[INST]Let's work this out in a step by step way to be sure we have the right answer.[/INST]
"""
CUSTOM_PROMPT = PromptTemplate(template=CUSTOM_PROMPT, input_variables=["question"])


class PlannerModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B-instruct"):
        super().__init__()
        self.__callbackManager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.maxOutputTokens = 2048
        self.temperature = 0.95
        self.top_p = 50
        self.n_gpu_layers = 40
        self.n_batch = 512
        self.__llm = LlamaCpp(
            model_path=cfg.models[modelName],
            temperature=self.temperature,
            max_tokens=self.maxOutputTokens,
            top_p=self.top_p,
            callback_manager=self.__callbackManager,
            n_gpu_layers=self.n_gpu_layers,
            n_batch=self.n_batch,
            verbose=True,  # Verbose is required to pass to the callback manager
        )
        self.__llmChain = LLMChain(prompt=CUSTOM_PROMPT, llm=self.__llm)
        self.modelName = modelName

        logging.info(f"Initialized planner model {modelName}")

    def execute(self, handler: ModelHandler):
        logging.info("Executing planner function")
        self.__modelHandler = handler
        messages = handler.messages()

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")

        # Get latest prompt + respond
        response = self.__llmChain.run(messages[-1]["content"])
        a = 1
        logging.info(f"Response generated")