# Base packages
import copy

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
        self.__model = Llama(model_path=cfg.models[modelName], n_gpu_layers=128, n_ctx=self.maxOutputTokens)

        logging.info(f"Initialized deny response model {modelName}")
    
    def execute(
        self, 
        handler: ModelHandler, 
        reason: str["irrelevant", "no_model"]) -> str:

        logging.info("Executing deny response function")
        self.__modelHandler = handler
        messages = handler.messages()
        tempMessages = copy.deepcopy(messages)

        # Get latest prompt + respond
        timePrompt = PromptTemplate(template=DENY_NO_MODEL_PROMPT, input_variables=["userPrompt"])
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