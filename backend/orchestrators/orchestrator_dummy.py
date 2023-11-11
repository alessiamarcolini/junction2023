import time

from model_handler.model_handler import ModelHandler
from orchestrators.orchestrator_base import OrchestratorBase


class Orchestrator(OrchestratorBase):
    def __init__(self):
        super().__init__()

    def execute(self, handler: ModelHandler):
        handler.update_status_message("started")
        time.sleep(2)
        handler.update_status_message("run_module_x")
        handler.update_progress_bar(0)

        time.sleep(2)
        handler.update_status_message("run_module_y")
        handler.update_progress_bar(50)
        handler.send_debug_thoughts("I answered this question because I am smart")

        time.sleep(2)
        handler.update_status_message(None)
        handler.update_progress_bar(-1)
        handler.send_debug_thoughts("If you would be as smart as me you would know this")

        handler.send_text("Hello world")
        time.sleep(2)
        handler.send_image("https://i.imgur.com/2X2IDEA.jpeg")
        time.sleep(2)
        for i in range(10):
            handler.send_text("Hello world")
            time.sleep(.1)
        time.sleep(2)
        handler.finalize()

        pass
