from modules.module_energy import EnergyModule
from model_handler.console_model_handler import ConsoleModelHandler

energyPredictions, energyPlot = EnergyModule().execute(horizon=180)
print(energyPredictions)
a = 1
# I'm going to Paris next week and I need to produce a time forecast for the energy prices for the next 3 months. Can you help me do that?