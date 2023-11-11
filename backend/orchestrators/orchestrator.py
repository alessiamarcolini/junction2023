from orchestrators.orchestrator_base import OrchestratorBase
from model_handler.model_handler import ModelHandler

class Orchestrator(OrchestratorBase):
    def __init__(self):
        Super().__init__()
    
    def execute(self, handler: ModelHandler):
        handler.update_status_message("Thinking...")

        