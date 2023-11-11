from modules.module_planner import PlannerModule
from model_handler.console_model_handler import ConsoleModelHandler

PlannerModule("mistral-7B-instruct").execute(ConsoleModelHandler())
# I want to know the price of steel in 6 weeks' time. Can you help me?