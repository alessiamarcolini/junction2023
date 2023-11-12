from modules.module_steel import SteelModule
from model_handler.console_model_handler import ConsoleModelHandler

steelPredictions, steelPlot = SteelModule().execute(horizon=3)
print(steelPredictions)
a = 1
# I'm going to Paris next week and I need to produce a time forecast for the energy prices for the next 3 months. Can you help me do that?