import time

from model_handler.model_handler import ModelHandler
from modules.module_energy import EnergyModule
from orchestrators.orchestrator_base import OrchestratorBase


class Orchestrator(OrchestratorBase):
    def __init__(self):
        super().__init__()

        self.energy_module = EnergyModule(model_name="WTF")

    def execute(self, handler: ModelHandler):
        handler.update_status_message("started")
        time.sleep(2)
        horizon = 9
        handler.update_status_message(f"run energy module, horizon {horizon}")
        handler.update_progress_bar(0)
        energy_predictions = self.energy_module.execute(horizon=horizon)
        handler.send_text(
            f"Energy prediction for horizon {horizon}: {energy_predictions}"
        )
        handler.finalize()
