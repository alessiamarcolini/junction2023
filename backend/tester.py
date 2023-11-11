from modules.module_deny import DenyModule
from model_handler.console_model_handler import ConsoleModelHandler

DenyModule(
    modelName="mistral-7B-instruct"
    ).execute(
        handler=ConsoleModelHandler(),
        reason="no_model"
        )
# I'm going to Paris next week and I need to produce a time forecast for the energy prices for the next 3 months. Can you help me do that?