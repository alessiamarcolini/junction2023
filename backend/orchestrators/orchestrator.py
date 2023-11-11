import logging

from orchestrators.orchestrator_base import OrchestratorBase
from model_handler.model_handler import ModelHandler
from modules.module_planner import PlannerModule

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
            logging.info("Explaining model output...")