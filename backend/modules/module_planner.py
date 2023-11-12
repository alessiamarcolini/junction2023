# Base packages
import logging
import copy
from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal
import json

# Own packages
from model_handler.model_handler import ModelHandler
from .module_base import ModuleBase
import config as cfg
from custom_types.orchestration_types import ExecutionReturn, OrchestrationPlan

# 3rd party packages
from llama_cpp import Llama
from langchain.prompts import PromptTemplate

DENY_PROMPT = """<s>[INST]
You are an assistant filtering inputs for further processing.
IF THE PROBLEM IS RELATED TO THE STEEL INDUSTRY OR ENERGY PRICES in any way,
you need to pass on the output for further processing. If the prompt is too
generic, please DECLINE the request. In all cases, generated a valid JSON
string with keys "reasoning" that justifies your "decision" (other key)
to DECLINE or PASS the request further.
[\INST]

Here are some examples:

Input: Can you generate some images of cats?
Output: {{
    "reasoning": "Generating images of cats is not related to the steel industry or energy prices.",
    "decision": "DECLINE"
}}
</s>

<s>
Input: I want to know the price of steel in 3 months.
Output: {{
    "reasoning": "Wanting to know the price of steel in three months is related to the steel industry.",
    "decision": "PASS"
}}
</s>

<s>
Input: How much energy does steel processing consume? Can you forecast factors influencing energy prices in the near future?
Output: {{
    "reasoning": "The first question is related to the steel industry, the second question is related to energy prices.",
    "decision": "PASS"
}}
</s>

<s>
Input: Can you help me generate some python code to print to the console?
Output: {{
    "reasoning": "Generating python code is not related to the steel industry or energy prices.",
    "decision": "DECLINE"
}}
</s>

<s>
Input: Hello! How are you doing?
Output: {{
    "reasoning": "This is a generic greeting, not related to the steel industry or energy prices.",
    "decision": "DECLINE"
}}
</s>

<s>
Input: Hey! This is a great question.
Output: {{
    "reasoning": "This is a generic greeting, not related to the steel industry or energy prices.",
    "decision": "DECLINE"
}}
</s>

Input: {userPrompt}
Output: """

MODEL_PROMPT = """<s>[INST]
You are an assistant who needs to decide whether it 
makes sense to apply a set of pre-trained machine learning
models to the problem. These models are:

ENERGY PRICE FORECAST MODEL: Predicts energy prices up to
12 months into the future.

STEEL PRICE FORECAST MODEL: Predicts steel alloy prices
up to 12 months into the future.

List ALL models applicable to the problem at hand. The Output
should include a list of relevant models. Additionally, you must 
argue in one sentence WHY YOU THINK THE MODELS YOU SELECTED ARE RELEVANT. [\INST]
Here are some examples:

Input: I want to know the price of purchasing steel in 6 weeks' time. Can you help me?
Output: {{
    "models" : ["STEEL PRICE FORECAST MODEL"],
    "reasoning": "Steel price directly impacts the purchase price."
}}
</s>

<s>
Input: Do you know how much energy it takes to produce steel?
Output: {{
    "models" : [],
    "reasoning": "The amount of energy required cannot be predicted by a price forecast model."
}}
</s>

<s>
Input: I want to know the energy costs for manufacturing steel in 6 weeks' time. Can you help me?
Output: {{
    "models" : ["ENERGY PRICE FORECAST MODEL"],
    "reasoning": "The energy price forecasting model directly predicts future energy costs."
}}
</s>

<s>
Input: I want to forecast the profit margin for producing steel for the next 2 months. Can you help me come up with an estimate?
Output: {{
    "models" : ["ENERGY PRICE FORECAST MODEL", "STEEL PRICE FORECAST MODEL"],
    "reasoning": "To calculate the profit, you need both a steel price forecast (revenue) and an energy price forecast (cost)."
}}
</s>

<s>
Input: I want to know the latest news about the steel industry. Can you summarize them for me please?
Output: {{
    "models" : [],
    "reasoning": "The forecasting models cannot be used to predict the news, only prices."
}}
</s>

Input: {userPrompt}
Output: """


class PlannerModule(ModuleBase):
    def __init__(self,
                 modelName: str = "mistral-7B-instruct"):
        super().__init__()
        self.maxOutputTokens = 2048
        self.temperature = 0.2
        self.top_p = 50
        self.n_gpu_layers = 40
        self.n_batch = 512
        self.modelName = modelName
        self.stream = False
        self.__maxRetries = 3
        self.__model = Llama(
            model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=self.maxOutputTokens)

        logging.info(f"Initialized planner model {modelName}")

    def execute(self, handler: ModelHandler) -> ExecutionReturn:
        logging.info("Executing planner function")
        self.__modelHandler = handler
        messages = handler.messages()
        tempMessages = copy.deepcopy(messages)

        # Get latest prompt + respond
        denyPrompt = PromptTemplate(
            template=DENY_PROMPT, input_variables=["userPrompt"])
        denyPrompt = denyPrompt.format(userPrompt=messages[-1]["content"])
        logging.info(f"Prompting model with: {denyPrompt}")
        tempMessages[-1]["content"] = denyPrompt

        # Task 1 - do we need to answer this message?
        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                tempMessages,
                max_tokens=128,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            logging.info(f"Deny/accept response {i} generated: {responseText}")

            try:
                denyResponse = json.loads(responseText)
            except json.decoder.JSONDecodeError:
                logging.warn(f"Model generated invalid JSON: {responseText}")
                continue

            try:
                # Stop generating when correct classification is achieved
                VALID_DECISIONS = ["DECLINE", "PASS"]
                if denyResponse["decision"] in VALID_DECISIONS:
                    logging.info(
                        f"Deny/accept response valid. Response: {json.dumps(denyResponse, indent=2)}")
                    break
            except Exception as e:
                logging.info(
                    f"Exception encountered when validating JSON contents: {e}")

        # Return: Question not relevant
        handler.send_debug_thoughts(denyResponse["reasoning"])
        if "decline" in responseText.lower():
            return {
                "orchestrationPlan": {
                    "goal": "deny",
                    "reasoning": "irrelevant"
                },
                "messages": messages,
            }

        # Task 2 - what models to use?
        logging.info("Executing model selector prompt")
        self.__modelHandler = handler
        tempMessages = copy.deepcopy(messages)

        # Create new prompt
        modelPrompt = PromptTemplate(
            template=MODEL_PROMPT, input_variables=["userPrompt"])
        modelPrompt = modelPrompt.format(userPrompt=messages[-1]["content"])
        logging.info(f"Prompting model with: {modelPrompt}")
        tempMessages[-1]["content"] = modelPrompt

        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                tempMessages,
                max_tokens=1024,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            logging.info(
                f"Model filter response {i} generated: {responseText}")

            try:
                modelResponse = json.loads(responseText)
            except json.decoder.JSONDecodeError:
                logging.warn(f"Model generated invalid JSON: {responseText}")
                continue

            try:
                # Stop generating when correct classification is achieved
                VALID_MODELS = ["ENERGY PRICE FORECAST MODEL",
                                "STEEL PRICE FORECAST MODEL"]
                if all(word in VALID_MODELS for word in modelResponse["models"]):
                    logging.info(
                        f"Model recommendations valid. Recommendations: {json.dumps(modelResponse, indent=2)}")
                    break
            except Exception as e:
                logging.info(
                    f"Exception encountered when validating JSON contents: {e}")

            if i + 1 == self.__maxRetries:
                raise RuntimeError("No usable response from LLM model")

        # Return output based on model use recommendations
        handler.send_debug_thoughts(modelResponse["reasoning"])
        if len(modelResponse["models"]) >= 1:
            return {
                "orchestrationPlan": {
                    "goal": "explain",
                    "reasoning": modelResponse["reasoning"],
                    "relevantModels": modelResponse["models"]
                },
                "messages": messages,
            }

        return {
            "orchestrationPlan": {
                "goal": "deny",
                "reasoning": "no_model",
            },
            "messages": messages,
        }
