# Base packages
import copy

# Custom packages
from .module_base import ModuleBase
from model_handler.model_handler import ModelHandler
from custom_types.orchestration_types import ExecutionReturn
import config as cfg
import logging

# 3rd party packages
from llama_cpp import Llama
from langchain.prompts import PromptTemplate

SUMMARY_PROMPT = """<s>[INST]
You are an assistant SUMMARIZING RESULTS from machine learning models
to aid busines decision-making. Please PROVIDE A SUMMARY OF 2-3 PARAGRAPHS
answering the following  Take it slow, calculate STEP BY STEP to make sure you are
correct. Here are some examples:
[/INST]

Input: {userPrompt}
Output: 
"""

class ExplainerModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B-instruct"):
        super().__init__()
        self.maxOutputTokens = 1024
        self.temperature = 0.2
        self.top_p = 50
        self.n_gpu_layers = 40
        self.n_batch = 512
        self.modelName = modelName
        self.stream = False
        self.__maxRetries = 3
        self.__model = Llama(model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=self.maxOutputTokens)

        logging.info(f"Initialized time model {modelName}")
    
    def execute(
        self,
        handler: ModelHandler,
        
        ) -> ExecutionReturn:
        logging.info("Executing time function")
        self.__modelHandler = handler
        messages = handler.messages()
        tempMessages = copy.deepcopy(messages)

        # Get latest prompt + respond
        timePrompt = PromptTemplate(template=TIME_PROMPT, input_variables=["userPrompt"])
        timePrompt = timePrompt.format(userPrompt=messages[-1]["content"])
        logging.info(f"Prompting time extraction model with: {timePrompt}")
        tempMessages[-1]["content"] = timePrompt

        # Task 1 - what is the timeframe of the request (in days)?
        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                tempMessages,
                max_tokens=128,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            logging.info(f"Time estimation response {i} generated: {responseText}")

            try:
                timeResponse = json.loads(responseText)
            except json.decoder.JSONDecodeError:
                logging.warn(f"Time estimation model generated invalid JSON: {responseText}")
                continue

            try:
                estimatedTime = int(timeResponse["days"])
                timeResponse["reasoning"]
                break
            except ValueError as e:
                logging.info(f"Exception encountered when validating JSON contents: {e}")
            except KeyError as e:
                logging.info(f"Generated response did not have all required keys: {e}")

            
            logging.info(f"Invalid time estimation model response. Retrying ... ({i}/{self.__maxRetries})")

            if i + 1 == self.__maxRetries:
                raise RuntimeError("No usable response from LLM model")
        
        # Return: Question not relevant
        handler.send_debug_thoughts(timeResponse["reasoning"])
        return timeResponse["days"]