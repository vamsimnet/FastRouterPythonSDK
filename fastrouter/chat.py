"""FastRouter chat API implementation"""

from typing import Dict, List, Optional, Any, Union
from .response_models import ChatCompletion, StreamingChatCompletion


class Completions:
    """Chat completions API"""
    
    def __init__(self, client):
        self._client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        stream: bool = False,
        provider: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Union[ChatCompletion, StreamingChatCompletion]:
        """
        Create a chat completion
        
        Args:
            model: The model to use for completion (e.g., "openai/gpt-4.1")
            messages: List of message objects with "role" and "content" keys
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            provider: Provider-specific configuration (e.g., {"only": ["azure"]})
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter (0-1)
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stop: Stop sequences
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response
        """
        # Build the request payload
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        # Add optional parameters if provided
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if provider is not None:
            payload["provider"] = provider
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        
        # Add any additional kwargs
        payload.update(kwargs)
        
        # Check if this is a streaming request
        is_streaming = payload.get('stream', False)
        
        # Make the API request
        if is_streaming:
            # For streaming, get raw response
            response = self._client._make_request(
                method="POST",
                endpoint="/api/v1/chat/completions",
                data=payload,
                stream=True
            )
            # Return streaming wrapper
            return StreamingChatCompletion(response, self._client)
        else:
            # For non-streaming, get JSON response
            response_data = self._client._make_request(
                method="POST",
                endpoint="/api/v1/chat/completions",
                data=payload,
                stream=False
            )
            # Return OpenAI-compatible response object
            return ChatCompletion(response_data)


class Chat:
    """Chat API namespace"""
    
    def __init__(self, client):
        self._client = client
        self.completions = Completions(client)
