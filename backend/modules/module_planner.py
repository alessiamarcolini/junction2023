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
Input: How much energy does steel processing consume? Can you forecast
factors influencing energy prices in the near future?
Output: PASS
</s>

<s>
Input: Can you help me generate some python code to print to the
console?
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
should be a valid JSON string with the following keys:
"models", "reasoning". "models" is simply a list of relevant models.
In "reasoning", you must argue in one sentence WHY YOU THINK 
THE MODELS YOU SELECTED ARE RELEVANT. [\INST]
Here are some examples:

Input: I want to know the price of purchasing steel in 6 weeks' time. Can you help me?
Output: {
    "models": ["STEEL PRICE FORECAST MODEL"],
    "reasoning": "Steel price directly impacts the purchase price."
}
</s>

<s>
Input: Do you know how much energy it takes to produce steel?
Output: {
    "models" : [],
    "reasoning": "The amount of energy required cannot be predicted by
a price forecast model."
}
</s>

<s>
Input: I want to know the energy costs for manufacturing steel in 6 weeks' time.
Can you help me?
Output: {
    "models": ["ENERGY PRICE MODEL"],
    "reasoning": "The energy price forecasting model directly predicts future energy costs."
}
</s>

<s>
Input: I want to forecast the profit margin for producing steel for the next 2 months.
Can you help me come up with an estimate?
Output: {
    "models": ["ENERGY PRICE FORECAST MODEL", "STEEL PRICE FORECAST MODEL"],
    "reasoning": "To calculate the profit, you need both a steel price forecast (revenue) and
an energy price forecast (cost)."
}
</s>

<s>
Input: I want to know the latest news about the steel industry. Can you summarize them
for me please?
Output: {
    "models" : [],
    "reasoning": "The forecasting models cannot be used to predict the news, only prices."
}
</s>

Input: """

BREAKDOWN_PROMPT_BEGIN = """<s>[INST]
You are an assistant and your task is to break down complex tasks into
a maximum of five smaller steps. Your output should be ONLY valid a JSON 
string: A list with each element as dictionary defining a sub-task

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
Output: [
    {
    "type": "LLM",
    "task": "Generate ideas for how to modernize equipment"
    }, {
    "type": "LLM",
    "task": "Generate ideas for how to optimize processes (waste heat
    management, energy management)"
    }, {
    "type": "LLM",
    "task": "Generate ideas for how to raise awareness among staff"
    }
]
</s>
"""

BREAKDOWN_ENERGY_PROMPT = """
<s>
Input: How can I improve my steel manufacturing company's profitability
in the next 12 weeks?
Output: [
    {
    "type": "LLM",
    "task": "Generate ideas for how to optimize processes"
    }, {
    "type": "ENERGY_PRICE_MODEL",
    "parameters": {
        "months": 3.0
    }
    },
    {
    "type": "LLM",
    "task": "Decide to purchase power in advance based on energy price model forecast"
    }
]
</s>
"""

BREAKDOWN_STEEL_PROMPT = """
<s>
Input: Should I produce more of steel alloy 10B in the two weeks?
Output: [
    {
    "type": "STEEL_PRICE_MODEL",
    "parameters": {
        "months": 0.5,
        "alloy": "10B"
    }
    },
    {
    "type": "LLM",
    "task": "Decide to produce more alloys based on steel price model forecast"
    }
]
</s>
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
        messages = copy.deepcopy(handler.messages())

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")
        messages[-1]["content"] = FILTER_PROMPT + messages[-1]["content"] + "\n Output:"

        # Task 1 - do we need to answer this message?
        for i in range(self.__maxRetries):
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
        messages = copy.deepcopy(handler.messages())
        logging.info(f"Deciding on models to use for prompt: {messages[-1]["content"]}")
        messages[-1]["content"] = MODEL_PROMPT + messages[-1]["content"] 

        # Add custom prompt to message
        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=128,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            logging.info(f"Filter response {i} generated: {responseText}")

            try:
                modelResponse = json.loads(responseText)
            except ValueError:
                logging.warn("Couldn't convert model recommendation to JSON. Retrying...")
                continue

            # Stop generating when correct classification is achieved
            acceptableResponses = ["forecast model", "none"]
            if any(word.lower() in acceptableResponses for word in modelResponse["models"]):
                logging.info(f"Model recommendations valid. Recommendations: {modelResponse["models"]}")
                break
        
        # Get models
        models = modelResponse["models"]

        # Load prompt in - again
        messages = copy.deepcopy(handler.messages())
        logging.info(f"Deciding on models to use for prompt: {messages[-1]["content"]}") 

        # Create breakdown prompt based on applicable models
        breakDownPrompt = BREAKDOWN_PROMPT_BEGIN
        breakDownPrompt += BREAKDOWN_ENERGY_MODEL if "energy price forecast model" in models else breakDownPrompt
        breakDownPrompt += BREAKDOWN_STEEL_MODEL if "steel price forecast model" in models else breakDownPrompt
        breakDownPrompt += BREAKDOWN_PROMPT_BASIC
        breakDownPrompt += BREAKDOWN_ENERGY_PROMPT if "energy price forecast model" in models else breakDownPrompt
        breakDownPrompt += BREAKDOWN_STEEL_PROMPT if "steel price forecast model" in models else breakDownPrompt
        breakDownPrompt += "Input: "
        logging.info(f"Problem breakdown prompt: {breakDownPrompt}")
        messages[-1]["content"] = breakDownPrompt + messages[-1]["content"]

        # Create orchestration plan
        for i in range(self.__maxRetries):
            filterResponse = self.__model.create_chat_completion(
                messages,
                max_tokens=128,
                stream=self.stream,
                temperature=self.temperature,
            )
            responseText = filterResponse['choices'][0]['message']['content']
            logging.info(f"Filter response {i} generated: {responseText}")

            try:
                orchestrationResponse = json.loads(responseText)
            except ValueError:
                logging.warn("Couldn't conver orchestration llm response to JSON")
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