from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

class ModelHandler:
    def __init__(self):
        pass

    def send_text(self, text):
        pass

    def send_image(self, image):
        pass

    def finalize(self):
        pass

    def messages(self) -> List[str]:
        pass

    def update_status_message(self, status: str) -> None:
        pass

    def update_progress_bar(self, progress: Union[int, None]) -> None:
        pass

    def send_debug_thoughts(self, thought: str) -> None:
        pass