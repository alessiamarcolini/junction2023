# Base packages
import copy
import logging

# Custom packages
from .module_base import ModuleBase
from model_handler.model_handler import ModelHandler
from custom_types.orchestration_types import ExecutionReturn, ModuleResults
from prompts.explainer_prompt import EXPLAINER_PROMPT
import config as cfg

# 3rd party packages
from llama_cpp import Llama
from langchain.prompts import PromptTemplate

INTRO_PROMPT = """<s>[INST]
You are an assistant SUMMARIZING RESULTS from machine learning models
to aid busines decision-making. Please PROVIDE A SUMMARY OF 2-3 PARAGRAPHS
answering the following  Take it slow, EXPLAIN STEP BY STEP to make sure you are
correct. Here are some examples:
[/INST]</s>
"""

SUMMARY_PROMPT = INTRO_PROMPT + EXPLAINER_PROMPT

class ExplainerModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B-instruct"):
        super().__init__()
        self.maxOutputTokens = 4096
        self.context = 8192
        self.temperature = 0.2
        self.top_p = 50
        self.n_gpu_layers = 40
        self.n_batch = 512
        self.modelName = modelName
        self.stream = True
        self.__maxRetries = 3
        self.__model = Llama(model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=self.context)

        logging.info(f"Initialized time model {modelName}")
    
    def execute(
        self,
        handler: ModelHandler,
        moduleResults: moduleResults,
        days: int,
        ) -> None:
        logging.info("Executing explainer function")
        self.__modelHandler = handler
        messages = handler.messages()
        tempMessages = copy.deepcopy(messages)

        # Get latest prompt + respond
        summaryPrompt = PromptTemplate(
            template=SUMMARY_PROMPT,
            input_variables=["userPrompt", "days", "steelPriceModel", "energyPriceModel"])
        summaryPrompt = summaryPrompt.format(
            userPrompt=messages[-1]["content"],
            days=days,
            steelPriceModel=moduleResults["steel"]["text"],
            energyPriceModel=moduleResults["energy"]["text"]
            )
        logging.info(f"Prompting summary model with: {summaryPrompt}")
        tempMessages[-1]["content"] = timePrompt

        responseStream = self.__model.create_chat_completion(
            tempMessages,
            max_tokens=self.maxOutputTokens,
            stream=self.stream,
            temperature=self.temperature,
        )
        result = []
        for output in responseStream:
            if output["choices"][0]["finish_reason"] is None:
                try:
                    word = output["choices"][0]["delta"]["content"]
                    handler.send_text(word)
                    result.append(word)

                except KeyError as e:
                    logging.info(f"Key error encountered for summary model output stream {e}")

        logging.info(f"Summary response generated: {result}")