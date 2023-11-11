# Base packages
import logging

# Own packages
from orchestrators.orchestrator_base import OrchestratorBase
from model_handler.model_handler import ModelHandler
from modules.module_planner import PlannerModule
from modules.module_time import TimeModule

# 3rd party packages
import numpy as np

class Orchestrator(OrchestratorBase):
    def __init__(self):
        Super().__init__()
    
    def execute(self, handler: ModelHandler):
        handler.update_status_message("Thinking...")
        planner = PlannerModule(
            modelName="mistral-7B-instruct"
        )

        logging.info("Planner initialized. Processing message...")
        orchestrationPlan = planner.execute(handler=handler)

        # Orchestration plan goal: "deny" or "explain"
        goal = orchestrationPlan["orchestrationPlan"]["goal"]

        # We have stuff to do
        if goal == "explain":
            handler.update_status_message("Preparing forecasts...")
            models = orchestrationPlan["orchestrationPlan"]["relevantModels"]
            logging.info(f"Explaining model output using models: {models}")

            # Get timeline for predictions
            days = TimeModule(
                modelName="mistral-7B-instruct"
            )

            # Convert days to months and round days/months
            months = np.ceil(days/30)
            days = np.ceil(days)

            # Call-out to energy module relevant modules
            moduleResults = {}
            if "ENERGY PRICE FORECAST MODEL" in models:
                handler.update_status_message(f"Running energy forecast for {days} days")
                
        # Update progress bar for deny request
        handler.update_progress_bar(50)