# Base packages
import logging
import copy
from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

# Own packages
from model_handler.model_handler import ModelHandler
from .module_base import ModuleBase
import config as cfg
from custom_types.orchestration_types import ExecutionReturn

# 3rd party packages
from llama_cpp import Llama
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import StrOutputParser

DENY_PROMPT = """<s>[INST]
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

Input: {userPrompt}
Output: """

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
Output: {
    models : [STEEL PRICE FORECAST MODEL],
    reasoning: Steel price directly impacts the purchase price.
}
</s>

<s>
Input: Do you know how much energy it takes to produce steel?
Output: {
    models : [],
    reasoning: The amount of energy required cannot be predicted by a price forecast model.
}
</s>

<s>
Input: I want to know the energy costs for manufacturing steel in 6 weeks' time. Can you help me?
Output: {
    models : [ENERGY PRICE FORECAST MODEL],
    reasoning: The energy price forecasting model directly predicts future energy costs.
}
</s>

<s>
Input: I want to forecast the profit margin for producing steel for the next 2 months. Can you help me come up with an estimate?
Output: {
    models : [ENERGY PRICE FORECAST MODEL, STEEL PRICE FORECAST MODEL],
    reasoning: To calculate the profit, you need both a steel price forecast (revenue) and an energy price forecast (cost).
}
</s>

<s>
Input: I want to know the latest news about the steel industry. Can you summarize them for me please?
Output: {
    models : [],
    reasoning: The forecasting models cannot be used to predict the news, only prices.
}
</s>

Input: {userPrompt}
Output: """

class PlannerModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B-instruct"):
        super().__init__()
        self.__callbackManager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.maxOutputTokens = 2048
        self.temperature = 0.2
        self.top_p = 50
        self.n_gpu_layers = 40
        self.n_batch = 512
        self.modelName = modelName

        logging.info(f"Initialized planner model {modelName}")

    def execute(self, handler: ModelHandler) -> ExecutionReturn:
        logging.info("Executing planner function")
        self.__modelHandler = handler
        messages = copy.deepcopy(handler.messages())

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")

        # Get latest prompt + respond
        denyPrompt = PromptTemplate(template=DENY_PROMPT, input_variables=["userPrompt"])
        llm = LlamaCpp(
            model_path=cfg.models[self.modelName],
            temperature=self.temperature,
            max_tokens=self.maxOutputTokens,
            top_p=self.top_p,
            callback_manager=self.__callbackManager,
            n_gpu_layers=self.n_gpu_layers,
            n_batch=self.n_batch,
            verbose=True,  # Verbose is required to pass to the callback manager
        )
        chain = LLMChain(prompt=denyPrompt, llm=llm)

        # Task 1 - do we need to answer this message?
        for i in range(self.__maxRetries):
            response = chain.run(userPrompt=messages[-1]['content'])
            logging.info(f"Deny/accept response {i} generated: {response}")

            if any(word in response.lower() for word in ["pass", "decline"]):
                logging.info(f"Correct deny/accept response generated")
                break
            
            logging.info(f"Invalid deny/accept response. Retrying ... ({i}/{self.__maxRetries})")

            if i + 1 == self.__maxRetries:
                raise RuntimeError("No usable response from LLM model")
        
        # Return: Question not relevant
        if "decline" in response.lower():
            newMessage = {
                "role": "system",
                "content": response,
            }
            messages.append(newMessage)

            return {
                "orchestrationPlan": {
                    "goal": "deny",
                    "reasoning": "Not relevant request"
                },
                "messages": messages,
            }


        # Task 2 - what models to use?
        logging.info("Executing model selector prompt")
        self.__modelHandler = handler
        messages = copy.deepcopy(handler.messages())

        # Add custom prompt to beginning of
        # last message
        logging.info(f"Latest message: {messages[-1]['content']}")

        # Get latest prompt + respond
        modelPrompt = PromptTemplate(template=MODEL_PROMPT, input_variables=["userPrompt"])
        llm = LlamaCpp(
            model_path=cfg.models[self.modelName],
            temperature=self.temperature,
            max_tokens=self.maxOutputTokens,
            top_p=self.top_p,
            callback_manager=self.__callbackManager,
            n_gpu_layers=self.n_gpu_layers,
            n_batch=self.n_batch,
            grammar_path=cfg.grammar["json"],
            verbose=True,  # Verbose is required to pass to the callback manager
        )
        chain = LLMChain(prompt=modelPrompt, llm=llm)

        for i in range(self.__maxRetries):
            response = chain.run(userPrompt=messages[-1]['content'])
            logging.info(f"Model filter response {i} generated: {response}")

            try:
                modelResponse = json.loads(response)
            except ValueError:
                logging.warn("Couldn't convert model recommendation to JSON. Retrying...")
                logging.info(f"Tried to convert: {response}")
                continue
            
            try:
                modelResponse["models"]
                modelResponse["reasoning"]
            except KeyError:
                logging.warn("Model output does not have appropriate keys")
                logging.info(f"Model output: {modelResponse}")

            if i + 1 == self.__maxRetries:
                raise RuntimeError("No usable response from LLM model")
