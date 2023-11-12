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
Question: What will the energy price be next month?
The steel price model made the following predictions for the next 1 month:
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
The model made the following predictions for the next 20 days:
    2019-01-01: 51.506606
    2019-01-02: 52.424759
    2019-01-03: 58.436885
    2019-01-04: 63.165417
    2019-01-05: 66.022342
    2019-01-06: 65.138907
    2019-01-07: 66.237986
    2019-01-08: 66.589283
    2019-01-09: 65.093596
    2019-01-10: 64.887763
    2019-01-11: 61.996093
    2019-01-12: 64.962063
    2019-01-13: 68.3111
    2019-01-14: 68.07991
    2019-01-15: 68.473804
    2019-01-16: 68.683759
    2019-01-17: 68.573591
    2019-01-18: 69.072635
    2019-01-19: 65.256993
    2019-01-20: 61.215024
    The previous 20 days had the following values:
    2018-12-12: 66.1
    2018-12-13: 58.17
    2018-12-14: 56.12
    2018-12-15: 69.13
    2018-12-16: 59.68
    2018-12-17: 56.16
    2018-12-18: 56.6
    2018-12-19: 58.04
    2018-12-20: 66.69
    2018-12-21: 64.24
    2018-12-22: 67.3
    2018-12-23: 70.56
    2018-12-24: 71.23
    2018-12-25: 71.98
    2018-12-26: 65.64
    2018-12-27: 72.61
    2018-12-28: 70.93
    2018-12-29: 65.49
    2018-12-30: 67.38
    2018-12-31: 68.4
    The model used the following features with the respective importances:
    price_actual_t-1: 0.128527
    total_load_actual_t-1: 0.032296
    season_t-3: 0.022793
    where, 
    - the feature 'price_actual_t-X' means the actual price from X days before.
    - the feature 'generation_fossil_hard_coal' represents the coal generation in MW,
    - the feature 'generation_fossil_brown_coal/lignite' represents the coal/lignite generation in MW.
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