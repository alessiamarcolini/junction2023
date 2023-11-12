# Base packages
import logging

# Own packages
from orchestrators.orchestrator_base import OrchestratorBase
from model_handler.model_handler import ModelHandler
from modules.module_planner import PlannerModule
from modules.module_time import TimeModule
from modules.module_energy import EnergyModule
from modules.module_steel import SteelModule
from modules.module_deny import DenyModule
from modules.module_explainer import ExplainerModule

# 3rd party packages
import numpy as np

class Orchestrator(OrchestratorBase):
    def __init__(self):
        super().__init__()
    
    def execute(self, handler: ModelHandler) -> None:
        handler.update_status_message("Thinking...")
        planner = PlannerModule(
            modelName="mistral-7B-instruct"
        )

        logging.info("Planner initialized. Processing message...")
        orchestrationPlan = planner.execute(handler=handler)

        # Orchestration plan goal: "deny" or "explain"
        goal = orchestrationPlan["orchestrationPlan"]["goal"]

        # Deny request (politely)
        if goal == "deny":
            handler.update_progress_bar(50)
            DenyModule(
                modelName="mistral-7B-instruct"
            ).execute(
                handler=handler,
                reason=orchestrationPlan["orchestrationPlan"]["reasoning"]
            )
            handler.update_progress_bar(100)
            handler.update_status_message("Done!")
            handler.finalize()
            return

        handler.update_status_message("Preparing forecasts...")
        models = orchestrationPlan["orchestrationPlan"]["relevantModels"]
        logging.info(f"Explaining model output using models: {models}")

        # Get timeline for predictions
        days = TimeModule(
            modelName="mistral-7B-instruct"
        ).execute(handler=handler)

        # Convert days to months and round days/months
        months = np.ceil(days/30)
        days = np.ceil(days)

        # Call-out to energy module relevant modules
        moduleResults = {
            "energy": {"text": ""},
            "steel": {"text": ""}
        }
        if "ENERGY PRICE FORECAST MODEL" in models:
            handler.update_status_message(f"Running energy forecast for {days} days...")
            logging.info(f"Running energy forecast for {days} days")
            energyPredictions, energyPlot = EnergyModule().execute(horizon=days)

            moduleResults["energy"] = {
                "text": energyPredictions,
                "plot": energyPlot
            }
        
        if "STEEL PRICE FORECAST MODEL" in models:
            handler.update_status_message(f"Running steel forecast for {months} months...")
            logging.info(f"Running steel forecast for {months} months")
            steelPredictions, steelPlot = SteelModule(
                model_name="Steel"
            ).execute(horizon=months)

            moduleResults["steel"] = {
                "text": steelPredictions,
                "plot": steelPlot
            }

        # Generate model summary
        handler.update_progress_bar(50)
        ExplainerModule(
            modelName="mistral-7B-instruct"
        ).execute(
            handler=handler,
            moduleResults=moduleResults,
            days=days
        )
        handler.update_progress_bar(100)
        handler.update_status_message("Done!")
        handler.finalize()
        
            