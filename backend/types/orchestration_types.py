from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

class OrchestrationStep(TypedDict):
    role: Literal["function", "summary"]
    name: Literal["decline", "summary", "energy_forecast", "price_forecast"]
    reason: str
    parameters: Optional[Dict[any]]