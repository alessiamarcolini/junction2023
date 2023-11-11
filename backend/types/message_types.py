from typing import Any, List, Optional, Dict, Union
from typing_extensions import TypedDict, NotRequired, Literal

class ChatCompletionRequestMessageContentPartText(TypedDict):
    type: Literal["text"]
    text: str


class ChatCompletionRequestMessageContentPartImageImageUrl(TypedDict):
    url: str
    detail: NotRequired[Literal["auto", "low", "high"]]


class ChatCompletionRequestMessageContentPartImage(TypedDict):
    type: Literal["image_url"]
    image_url: Union[str, ChatCompletionRequestMessageContentPartImageImageUrl]


ChatCompletionRequestMessageContentPart = Union[
    ChatCompletionRequestMessageContentPartText,
    ChatCompletionRequestMessageContentPartImage,
]

class ChatCompletionRequestSystemMessage(TypedDict):
    role: Literal["system"]
    content: Optional[str]


class ChatCompletionRequestUserMessage(TypedDict):
    role: Literal["user"]
    content: Optional[Union[str, List[ChatCompletionRequestMessageContentPart]]]


class ChatCompletionRequestFunctionMessage(TypedDict):
    role: Literal["function"]
    content: Optional[str]
    name: str


ChatCompletionRequestMessage = Union[
    ChatCompletionRequestSystemMessage,
    ChatCompletionRequestUserMessage,
    ChatCompletionRequestFunctionMessage,
]