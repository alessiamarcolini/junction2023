from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

from custom_types.message_types import ChatCompletionRequestMessage

class OrhestrationPlan(TypedDict):
    goal: Literal["deny", "explain"]
    reasoning: str
    relevantModels: NotRequired[Literal["energy_price", "steel_price"]]

class ExecutionReturn(TypedDict):
    orchestrationPlan: OrhestrationPlan
    messages: List[ChatCompletionRequestMessage]
