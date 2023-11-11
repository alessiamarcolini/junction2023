# Base packages
from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal
import logging
import copy
import json

# Custom packages
from backend.model_handler.model_handler import ModelHandler
from backend.modules.module_base import ModuleBase
from backend.types.orchestration_types import OrchestrationStep
import backend.config as cfg

# 3-rd party packages
from llama_cpp import Llama

FILTER_PROMPT = """<s>[INST]
You are an assistant filtering inputs for further processing.
IF THE PROBLEM IS RELATED TO THE STEEL INDUSTRY in any way,
you need to pass on the output for further processing. In these cases,
only generate one word: "PASS". Otherwise, you need to return the
word "DECLINE" for the request. RETURN ONLY ONE WORD.
[\INST]

Here are some examples:

Input: Can you generate some images of cats?
Output: DECLINE
</s>

<s>
Input: I want to know the price of steel in 3 months.
Output: PASS
</s>

<s>
Input: How much energy does steel processing consume? Can you forecast factors influencing energy prices in the near future?
Output: PASS
</s>

<s>
Input: Can you help me generate some python code to print to the console?
Output: DECLINE
</s>

Input: """

MODEL_PROMPT = """<s>[INST]
You are an assistant who needs to decide whether it 
makes sense to apply a set of pre-trained machine learning
models to the problem. These models are:

ENERGY PRICE FORECAST MODEL: Predicts energy prices up to
6 months into the future.

STEEL PRICE FORECAST MODEL: Predicts steel alloy prices
up to 6 months into the future.

List ALL models applicable to the problem at hand. The Output
should include a list of relevant models. Additionally, you must 
argue in one sentence WHY YOU THINK THE MODELS YOU SELECTED ARE RELEVANT. [\INST]
Here are some examples:

Input: I want to know the price of purchasing steel in 6 weeks' time. Can you help me?
Models: STEEL PRICE FORECAST MODEL,
Reasoning: Steel price directly impacts the purchase price.
</s>

<s>
Input: Do you know how much energy it takes to produce steel?
Models : NONE,
Reasoning: The amount of energy required cannot be predicted by a price forecast model.
</s>

<s>
Input: I want to know the energy costs for manufacturing steel in 6 weeks' time. Can you help me?
Models: ENERGY PRICE MODEL,
Reasoning: The energy price forecasting model directly predicts future energy costs.
</s>

<s>
Input: I want to forecast the profit margin for producing steel for the next 2 months. Can you help me come up with an estimate?
Models: ENERGY PRICE FORECAST MODEL, STEEL PRICE FORECAST MODEL,
Reasoning: To calculate the profit, you need both a steel price forecast (revenue) and an energy price forecast (cost).
</s>

<s>
Input: I want to know the latest news about the steel industry. Can you summarize them for me please?
Models : NONE,
Reasoning: The forecasting models cannot be used to predict the news, only prices.
</s>

Input: """

BREAKDOWN_PROMPT_BEGIN = """<s>[INST]
You are an assistant and your task is to break down complex tasks into
a maximum of five smaller steps. Your output should be ONLY a list with 
each element on a new line.

Please incorporate ALL of the following models into your analysis and
provide appropriate inputs to them using a dictionary with type and input
parameters in JSON format:
- LLM: Large language model for creative ideation and evaluation
    Parameters:
    - task (string): Prompt for the model.
"""

BREAKDOWN_ENERGY_MODEL = """
- ENERGY_PRICE_MODEL: Predicts energy prices up to
6 months into the future.
    Parameters:
    - months (float): Predict for this many months ahead from
    the present.
"""

BREAKDOWN_STEEL_MODEL = """
- STEEL PRICE FORECAST MODEL: Predicts steel alloy prices
up to 6 months into the future.
    Parameters:
    - months (float): Predict for this many months ahead from
    the present.
    - alloy (string): Name of steel alloy to predict prices for.
"""

BREAKDOWN_PROMPT_BASIC = """[/INST]
Here are some examples to help you:

Input: How can I improve energy efficiency in steel manufacturing?
Output: 
LLM - Task: Generate ideas for how to modernize equipment,
LLM - Task: Generate ideas for how to optimize processes (waste heat management, energy management),
LLM - Task: Generate ideas for how to raise awareness among staff
</s>
"""

BREAKDOWN_ENERGY_PROMPT = """
<s>
Input: How can I improve my steel manufacturing company's profitability
in the next 12 weeks?
Output: 
LLM - Task: Generate ideas for how to optimize processes, 
ENERGY_PRICE_MODEL - Months: 3.0
LLM - Task: Decide to purchase power in advance based on energy price model forecast
</s>
"""

BREAKDOWN_STEEL_PROMPT = """
<s>
Input: Should I produce more of steel alloy 10B in the two weeks?
Output: 
STEEL_PRICE_MODEL - Months: 0.5 ; Alloy: "10B"
LLM - Task: Decide to produce more alloys based on steel price model forecast
</s>
"""

class PlannerModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B-instruct",
        maxRetries: int = 3):
        super().__init__()
        self.__model = Llama(model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=2048)
        self.__maxRetries = maxRetries
        self.modelName = modelName
        self.stream = False
        self.temperature = 0.95

        logging.info(f"Initialized planner model {modelName}")

    def execute(self, handler: ModelHandler) -> List[OrchestrationStep]:
        logging.info("Executing planner function")
        self.__modelHandler = handler
        messages = copy.deepcopy(handler.messages())

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")
        messages[-1]["content"] = FILTER_PROMPT + messages[-1]["content"] + "\n Output:"

        # Task 1 - do we need to answer this message?
        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=16,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content'].lower()
            logging.info(f"Accept/deny response {i} generated: {responseText}")

            if any(word in responseText for word in ["pass", "decline"]):
                logging.info(f"Correct response generated: {responseText}")
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
        messages = copy.deepcopy(handler.messages())
        logging.info(f"Deciding on models to use for prompt: {messages[-1]["content"]}")
        messages[-1]["content"] = MODEL_PROMPT + messages[-1]["content"] 

        # Task 2 - what models to use?
        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=128,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            responseText.lstrip("Output: ")
            logging.info(f"Model filter response {i} generated: {responseText}")

            try:
                modelResponse = json.loads(responseText)
            except ValueError:
                logging.warn("Couldn't convert model recommendation to JSON. Retrying...")
                logging.info(f"Tried to convert: {responseText}")
                continue

            # Stop generating when correct classification is achieved
            acceptableResponses = ["forecast model", "none"]
            if any(word.lower() in acceptableResponses for word in modelResponse["models"]):
                logging.info(f"Model recommendations valid. Recommendations: {json.dumps(modelResponse, indent=2)}")
                break
        
        # Get models
        models = modelResponse["models"]

        # Load prompt in - again
        messages = copy.deepcopy(handler.messages())
        logging.info(f"Deciding on models to use for prompt: {messages[-1]["content"]}") 

        # Create breakdown prompt based on applicable models
        breakDownPrompt = BREAKDOWN_PROMPT_BEGIN
        if "energy price forecast model" in models:
            breakDownPrompt += BREAKDOWN_ENERGY_MODEL
        if "steel price forecast model" in models:
            breakDownPrompt += BREAKDOWN_STEEL_MODEL
        breakDownPrompt += BREAKDOWN_PROMPT_BASIC
        if "energy price forecast model" in models:
            breakDownPrompt += BREAKDOWN_ENERGY_PROMPT
        if "steel price forecast model" in models:
            breakDownPrompt += BREAKDOWN_STEEL_PROMPT
        breakDownPrompt += "Input: "
        logging.info(f"Problem breakdown prompt: {breakDownPrompt}")
        messages[-1]["content"] = breakDownPrompt + messages[-1]["content"]

        # Task 3 - Create orchestration plan
        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=128,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            responseText.lstrip("Output: ")
            logging.info(f"Orchestration response {i} generated: {responseText}")

            try:
                orchestrationResponse = json.loads(responseText)
            except ValueError:
                logging.warn("Couldn't conver orchestration llm response to JSON. Retrying...")
                logging.info(f"Tried to convert: {responseText}")
                continue

            # Validate output
            for module in orchestrationResponse:
                if module["type"].lower() == "llm":
                    try:
                        module["task"]
                    except KeyError:
                        logging.info("Orchestration definition does not contain task for llm. Retrying...")
                        continue
                
                elif module["type"].lower == "steel_price_model":
                    try:
                        module["months"]
                        module["alloy"]
                    except KeyError:
                        logging.info("Orchestration definition does not contain correct keys for steel price model. Retrying...")
                        continue
                
                else:
                    try:
                        module["months"]
                    except KeyError:
                        logging.info("Orchestration definition does not contain correct keys for energy price model. Retrying...")
                        continue

        # Return orchestration plan
        logging.info("Orchestration plan created:")
        logging.info(json.dumps(orchestrationResponse, indent=2))

        return orchestrationResponse