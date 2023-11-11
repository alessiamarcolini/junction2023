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
answering the following  Take it slow, EXPLAIN STEP BY STEP to make sure you are
correct. Here are some examples:
[/INST]</s>

<s>
Time: Today is 12 November 2023.
Question: What will the energy price be next month?
The steel price model made the following predictions for the next 3 months:
    2023-10-01: 171.7189999999999
    2023-11-01: 171.38899999999987
    2023-12-01: 171.40699999999987The previous 3 months had the following values:
    2023-07-01: 161.3
    2023-08-01: 158.9
    2023-09-01: 157.0The model used the following features with the respective importances:Germany_steel_index_t-0: 0.2839260308502419
    Germany_steel_index_t-1: 0.310658020913513
    Germany_steel_index_t-2: 0.3052224592438692
    Germany_electricity_index_t-0: 0.0741619640668506
    Germany_electricity_index_t-1: 0.021995389702004323
    Germany_electricity_index_t-2: 0.004036135223521021Short-term business statistics (STS) provide index data on various economic activities. Percentage changes,
    The column Germany_steel_index represents the STS for Basic iron and steel and ferro-alloys
    The column Germany_electricity_index represents the STS for Electricity
    The t-x where x represents the delay in the features e-g t-1 represents the previous months data in the given column 
The energy price model made the following predictions for the next 3 months: 
</s>

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