"""FastRouter Python SDK"""

from .client import FastRouter
from .exceptions import FastRouterError, APIError, AuthenticationError

__version__ = "0.1.0"
__all__ = ["FastRouter", "FastRouterError", "APIError", "AuthenticationError"]
