"""OpenAI-compatible response models for FastRouter SDK"""

from typing import Dict, List, Any, Optional, Union, Iterator
import json


class Usage:
    """Usage statistics for the completion"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self.chat_id = data.get('chat_id')
        self.completion_tokens = data.get('completion_tokens', 0)
        self.prompt_tokens = data.get('prompt_tokens', 0) 
        self.total_tokens = data.get('total_tokens', 0)
        self.cost = data.get('cost', 0.0)
        self.provider = data.get('provider')
        self.completion_tokens_details = data.get('completion_tokens_details', {})
        self.prompt_tokens_details = data.get('prompt_tokens_details', {})
    
    def __repr__(self):
        return f"Usage(completion_tokens={self.completion_tokens}, prompt_tokens={self.prompt_tokens}, total_tokens={self.total_tokens})"


class Message:
    """Chat message object"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self.role = data.get('role', '')
        self.content = data.get('content', '')
        self.annotations = data.get('annotations', [])
    
    def __repr__(self):
        return f"Message(role='{self.role}', content='{self.content[:50]}{'...' if len(self.content) > 50 else ''}')"


class Choice:
    """Individual choice in the completion response"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self.index = data.get('index', 0)
        self.message = Message(data.get('message', {}))
        self.finish_reason = data.get('finish_reason')
    
    def __repr__(self):
        return f"Choice(index={self.index}, message={self.message}, finish_reason='{self.finish_reason}')"


class ChatCompletion:
    """Main chat completion response object - OpenAI compatible"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data  # Keep original data for backward compatibility
        
        # Core OpenAI-compatible fields
        self.id = data.get('id', '')
        self.object = data.get('object', 'chat.completion')
        self.created = data.get('created')
        self.model = data.get('model', '')
        self.service_tier = data.get('service_tier', 'default')
        
        # Choices - convert to Choice objects
        choices_data = data.get('choices', [])
        self.choices = [Choice(choice) for choice in choices_data]
        
        # Usage statistics
        usage_data = data.get('usage', {})
        self.usage = Usage(usage_data) if usage_data else None
        
        # FastRouter-specific fields
        self.guardrails = data.get('guardrails', {})
        self.citations = data.get('citations')
    
    def __repr__(self):
        return f"ChatCompletion(id='{self.id}', model='{self.model}', choices={len(self.choices)})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the original dictionary representation for backward compatibility"""
        return self._data


class HealthResponse:
    """Health check response object"""
    
    def __init__(self, data: Union[Dict[str, Any], str]):
        if isinstance(data, str):
            self._data = {"status": data}
            self.status = data
        else:
            self._data = data
            self.status = data.get('status', data.get('content', 'Unknown'))
    
    def __repr__(self):
        return f"HealthResponse(status='{self.status}')"
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation"""
        return self._data


# Streaming response models

class Delta:
    """Delta object for streaming responses"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self.role = data.get('role')
        self.content = data.get('content', '')
    
    def __repr__(self):
        return f"Delta(role={self.role}, content='{self.content[:30]}{'...' if len(self.content) > 30 else ''}')"


class ChoiceChunk:
    """Individual choice in a streaming response chunk"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        self.index = data.get('index', 0)
        self.delta = Delta(data.get('delta', {}))
        self.finish_reason = data.get('finish_reason')
    
    def __repr__(self):
        return f"ChoiceChunk(index={self.index}, delta={self.delta}, finish_reason='{self.finish_reason}')"


class ChatCompletionChunk:
    """Individual chunk in a streaming chat completion response"""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = data
        
        # Core fields
        self.id = data.get('id', '')
        self.object = data.get('object', 'chat.completion.chunk')
        self.created = data.get('created')
        self.model = data.get('model', '')
        
        # Choices - convert to ChoiceChunk objects, ensure it's always a list
        choices_data = data.get('choices', [])
        if not isinstance(choices_data, list):
            choices_data = []
        self.choices = [ChoiceChunk(choice) for choice in choices_data]
        
        # Usage (usually only in final chunk)
        usage_data = data.get('usage', {})
        self.usage = Usage(usage_data) if usage_data else None
    
    def __repr__(self):
        return f"ChatCompletionChunk(id='{self.id}', model='{self.model}', choices={len(self.choices)})"
    
    @property
    def has_content(self) -> bool:
        """Check if this chunk has actual content"""
        if not self.choices or len(self.choices) == 0:
            return False
        
        content = self.choices[0].delta.content
        return content is not None and content.strip() != ''
    
    @property
    def content(self) -> str:
        """Safely get content from first choice, or empty string"""
        if self.has_content:
            return self.choices[0].delta.content
        return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the original dictionary representation"""
        return self._data


class StreamingChatCompletion:
    """Streaming chat completion response - iterable"""
    
    def __init__(self, response, client):
        self.response = response
        self.client = client
        self._iterator = None
    
    def __iter__(self):
        """Make this object iterable"""
        self._iterator = self._parse_stream()
        return self
    
    def __next__(self):
        """Get next chunk from stream"""
        if self._iterator is None:
            self._iterator = self._parse_stream()
        return next(self._iterator)
    
    def _parse_stream(self) -> Iterator[ChatCompletionChunk]:
        """Parse Server-Sent Events stream"""
        try:
            for line in self.response.iter_lines(decode_unicode=True):
                if line:
                    line = line.strip()
                    
                    # SSE format: "data: {json}"
                    if line.startswith('data: '):
                        data_part = line[6:]  # Remove "data: " prefix
                        
                        # Check for end of stream
                        if data_part.strip() == '[DONE]':
                            break
                        
                        try:
                            # Parse JSON chunk
                            chunk_data = json.loads(data_part)
                            yield ChatCompletionChunk(chunk_data)
                        except json.JSONDecodeError:
                            # Skip malformed chunks
                            continue
                    
        except Exception as e:
            # If streaming fails, raise an appropriate error
            from .exceptions import FastRouterError
            raise FastRouterError(f"Streaming error: {str(e)}")
        finally:
            # Close the response
            if hasattr(self.response, 'close'):
                self.response.close()
