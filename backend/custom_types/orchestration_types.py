from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal
from pydantic import BaseModel

from custom_types.message_types import ChatCompletionRequestMessage

class OrhestrationPlan(BaseModel):
    goal: Literal["deny", "explain"]
    reasoning: str
    relevantModels: NotRequired[Literal["ENERGY PRICE FORECAST MODEL", "STEEL PRICE FORECAST MODEL"]]

class ExecutionReturn(TypedDict):
    orchestrationPlan: OrhestrationPlan
    messages: List[ChatCompletionRequestMessage]
