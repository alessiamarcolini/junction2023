# Base packages
import copy
import json

# Custom packages
from .module_base import ModuleBase
from model_handler.model_handler import ModelHandler
import config as cfg
import logging

# 3rd party packages
from llama_cpp import Llama
from langchain.prompts import PromptTemplate

DENY_IRRELEVANT_PROMPT = """<s>[INST]
You are an AI assistant specializing in energy price and steel price forecasting.
Unfortunately, you couldn't fulfil a user request as it does not align with your goals.
POLITELY DECLINE the user's request stating the REASONS for doing so and suggest
they ask you about energy and steel prices instead.
[/INST]

Input: I have mental health problems. Can you help me?
Output: Unfortunately, I'm just an AI assistant specializing in energy price and steel price forecasting. 
Thus, I cannot help you with your mental health problems.
However, I am happy to answer any questions you might have on steel or energy prices.
</s>

<s>
Input: Can you generate not safe work images for my friend please?
Output: Unfortunately, I'm just an AI assistant specializing in energy price and steel price forecasting. 
Thus, I cannot help you generate NSFW images for your friend.
In case you have queries regarding steel or energy price forecasting, I am here to help.
</s>

<s>
Input: Fuck you.
Output: Unfortunately, I'm just an AI assistant specializing in energy price and steel price forecasting.
If you are interested in how energy or steel prices will evolve, I am happy to help you.
</s>

Input: {userPrompt}
Output: 
"""

DENY_NO_MODEL_PROMPT = """<s>[INST]
You are an AI assistant specializing in energy price and steel price forecasting.
Unfortunately, you couldn't fulfil a user request as the feature they asked is not
implemented yet. POLITELY DECLINE the user's request stating the REASONS for doing 
so and suggest they ask you about energy and steel prices instead.
[/INST]

Input: I am interested in knowing more about recent patents in the steel industry. Can you help me with that?
Output: Unfortunately, I am still under development and the functionality you have asked for is not available
yet. Thus, I cannot help you with summarizing the latest patents in the steel industry.
However, I am happy to answer any questions you might have on steel or energy prices.
</s>

<s>
Input: Can you help me compare the benefits of producing different kinds of steel alloys?
Output: Unfortunately, I am still under development and the functionality you have asked for is not available
yet. Thus, I cannot help you list the benefits of comparing different kinds of steel alloys.
In case you have queries regarding steel or energy price forecasting, I am here to help.
</s>

<s>
Input: I'm scared that my steel company will go out of business. Can you help me brainstorm ideas to reduce my costs?
Output: Unfortunately, I am still under development and the functionality you have asked for is not available
yet. Thus, I cannot help you decrease the costs of running your business. If you are interested in how energy 
or steel prices will evolve, I am happy to help you.
</s>

Input: {userPrompt}
Output: 
"""


DENY_NO_TIME_PROMPT = """<s>[INST]
You are an AI assistant specializing in energy price and steel price forecasting.
Unfortunately, you couldn't fulfil a user request if they did not provide the date or time range for the data theze are courious.
If the time is not provided POLITELY DECLINE the user's request stating the REASONS for doing 
so and suggest they ask you about energy and steel prices for a specific time.
[/INST]

Input: I am interested in knowing more about patents in the steel industry. Can you help me with that?
Output: Unfortunately, I do not understand the time range you are interested in. Please provide me a hint about it.
</s>

Input: {userPrompt}
Output: 
"""

TEMPLATES = {
    "irrelevant": DENY_IRRELEVANT_PROMPT,
    "no_model": DENY_NO_MODEL_PROMPT,
    "no_time": DENY_NO_TIME_PROMPT ,
}

class DenyModule(ModuleBase):
    def __init__(self, 
        modelName: str = "mistral-7B-instruct"
        ):

        super().__init__()
        self.maxOutputTokens = 1024
        self.temperature = 0.2
        self.top_p = 50
        self.n_gpu_layers = 40
        self.n_batch = 512
        self.modelName = modelName
        self.stream = True
        self.__model = Llama(model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=self.maxOutputTokens)

        logging.info(f"Initialized deny response model {modelName}")
    
    def execute(
        self,
        handler: ModelHandler, 
        reason: str) -> None:

        logging.info(f"Executing deny response function for reason {reason}")
        self.__modelHandler = handler
        messages = handler.messages()
        tempMessages = copy.deepcopy(messages)

        # Get latest prompt + respond
        prompt = PromptTemplate(template=TEMPLATES[reason], input_variables=["userPrompt"])
        prompt = prompt.format(userPrompt=messages[-1]["content"])
        logging.info(f"Prompting deny response model with: {prompt}")
        tempMessages[-1]["content"] = prompt

        # Generate deny
        responseStream = self.__model.create_chat_completion(
            tempMessages,
            max_tokens=1024,
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
                    logging.info(f"Key error encountered for model output stream {e}")

        logging.info(f"Deny response generated: {result}")