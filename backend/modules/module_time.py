# Base packages
import copy
import json

# Custom packages
from .module_base import ModuleBase
from model_handler.model_handler import ModelHandler
from custom_types.orchestration_types import ExecutionReturn
import config as cfg
import logging

# 3rd party packages
from llama_cpp import Llama
from langchain.prompts import PromptTemplate

TIME_PROMPT = """<s>[INST]
You are an assistant EXTRACTing TIME INFORMATION from forecast requests.
You need to create a valid JSON file with the keys "reasoning" which
details how you calculated the number of days the prediction is in 
the future. Take it slow, calculate STEP BY STEP to make sure you are
correct. Here are some examples:
[/INST]

Input: I want to know the price of energy 2 weeks from now.
Output: {{
    "reasoning": "The request mentions '2 weeks from now'. Thus the number of days is 2 weeks x 7 days = 14 days.",
    "days": 14
}}
</s>

<s>
Input: How are steel alloys going to be priced in 1-2 months' time?
Output:{{
    "reasoning": "The request mentions `1-2 months time`. I assume a month is 30 days and I take the further point of 2 months. Thus the number of days is 2 months x 30 days = 60 days",
    "days": 60
}}
</s>

<s>
Input: I'm going to the doctor tomorrow and need to know the energy prices for next month.
Output:{{
    "reasoning": "The request mentions `for next month`. I assume a month is 30 days and I take the furthest point of a full month. Thus the number of days is 1 month x 30 days = 30 days",
    "days": 30
}}
</s>

<s>
Input: I came to work early at 7am and now I need an energy price forecast for the next half week. Can you help with that?
Output:{{
    "reasoning": "The request mentions `for the next half week`. A week is 7 days and thus half of a week is 0.5 weeks x 7 days = 3.5 days. Rounding it up gives 4 days",
    "days": 4
}}
</s>

<s>
Input: What is the price of steel, is it cheap or is it expensive?
Output:{{
    "reasoning": "The requested information can not be used as a time reference. Thus, I can not extract a time reference from the request.",
    "days": null
}}
</s>

Input: {userPrompt}
Output: 
"""


class TimeModule(ModuleBase):
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
        self.__model = Llama(
            model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=self.maxOutputTokens)

        logging.info(f"Initialized time model {modelName}")

    def execute(self, handler: ModelHandler) -> float:
        logging.info("Executing time function")
        self.__modelHandler = handler
        messages = handler.messages()
        tempMessages = copy.deepcopy(messages)

        # Get latest prompt + respond
        timePrompt = PromptTemplate(
            template=TIME_PROMPT, input_variables=["userPrompt"])
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
            logging.info(
                f"Time estimation response {i} generated: {responseText}")

            try:
                timeResponse = json.loads(responseText)
            except json.decoder.JSONDecodeError:
                logging.warn(
                    f"Time estimation model generated invalid JSON: {responseText}")
                continue

            try:
                estimatedTime = int(timeResponse["days"])
                timeResponse["reasoning"]
                break
            except ValueError as e:
                logging.info(
                    f"Exception encountered when validating JSON contents: {e}")
            except KeyError as e:
                logging.info(
                    f"Generated response did not have all required keys: {e}")
            except TypeError as e:
                logging.info(
                    f"Generated response did not have required type: {e}")
                if timeResponse["days"] is None:
                    handler.send_debug_thoughts(timeResponse["reasoning"])
                    return timeResponse

            logging.info(
                f"Invalid time estimation model response. Retrying ... ({i}/{self.__maxRetries})")

            if i + 1 == self.__maxRetries:
                raise RuntimeError("No usable response from LLM model")

        # Return: Question not relevant
        handler.send_debug_thoughts(timeResponse["reasoning"])
        return timeResponse
