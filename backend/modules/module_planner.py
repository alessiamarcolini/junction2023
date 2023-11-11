# Base packages
import logging
import copy
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

    def execute(self, handler: ModelHandler):
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
            response = chain.run(userPrompt=messages[-1]['content']).lower()
            logging.info(f"Deny/accept response {i} generated: {response}")

            if any(word in response for word in ["pass", "decline"]):
                logging.info(f"Correct deny/accept response generated")
                break
            
            logging.info(f"Invalid deny/accept response. Retrying ... ({i}/{self.__maxRetries})")
        

        # Task 2 - Generate answer template
        logging.info(f"Response generated: {response}")