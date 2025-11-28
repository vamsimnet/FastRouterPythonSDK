"""FastRouter Python SDK"""

from .client import FastRouter
from .exceptions import FastRouterError, APIError, AuthenticationError
from .response_models import (
    ChatCompletion, 
    Choice, 
    Message, 
    Usage, 
    HealthResponse,
    ChatCompletionChunk,
    ChoiceChunk,
    Delta,
    StreamingChatCompletion
)

__version__ = "0.1.4"
__all__ = [
    "FastRouter", 
    "FastRouterError", 
    "APIError", 
    "AuthenticationError",
    "ChatCompletion",
    "Choice", 
    "Message", 
    "Usage",
    "HealthResponse",
    "ChatCompletionChunk",
    "ChoiceChunk",
    "Delta",
    "StreamingChatCompletion"
]
