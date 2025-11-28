"""FastRouter client implementation"""

import json
import requests
from typing import Dict, List, Optional, Any, Union
from .exceptions import FastRouterError, APIError, AuthenticationError
from .response_models import HealthResponse
from .chat import Chat


class FastRouter:
    """Main FastRouter client class"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.fastrouter.ai",
        timeout: float = 30.0
    ):
        """
        Initialize FastRouter client.
        
        Args:
            api_key: Your FastRouter API key. If None, will try to get from environment.
            base_url: Base URL for the FastRouter API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or self._get_api_key_from_env()
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Initialize nested clients
        self.chat = Chat(self)
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variable"""
        import os
        return os.getenv('FASTROUTER_API_KEY')
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        return headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Any]:
        """
        Make HTTP request to FastRouter API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request payload for POST/PUT requests
            params: Query parameters
            stream: Whether this is a streaming request
            
        Returns:
            Response JSON data or raw response for streaming
            
        Raises:
            AuthenticationError: For 401 errors
            APIError: For other API errors
            FastRouterError: For other errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params,
                timeout=self.timeout,
                stream=stream  # Enable streaming if requested
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code >= 400:
                # For errors, always try to parse JSON (even for streaming requests)
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        # Get error object, ensure it's a dict before calling .get() again
                        error_obj = error_data.get('error', {})
                        if isinstance(error_obj, dict):
                            error_message = error_obj.get('message', 'Unknown API error')
                        elif isinstance(error_obj, str):
                            error_message = error_obj
                        else:
                            error_message = str(error_obj) if error_obj else 'Unknown API error'
                    else:
                        error_message = str(error_data)
                except (ValueError, KeyError, AttributeError) as e:
                    # Add debug info to help track down the issue
                    error_message = f"HTTP {response.status_code}: {response.text} (Parse error: {str(e)})"
                raise APIError(error_message, status_code=response.status_code)
            
            # If this is a streaming request, return the raw response
            if stream:
                return response
            
            # Try to parse JSON response
            try:
                json_response = response.json()
                # Debug: print response type and content for troubleshooting (disabled)
                # print(f"DEBUG: Response type: {type(json_response)}, Content: {json_response}")
                
                # Ensure we always return a dictionary
                if isinstance(json_response, dict):
                    # Check if this is actually an error response disguised as success
                    if 'error' in json_response:
                        # This might be an error response with 200 status - handle it properly
                        error_obj = json_response.get('error', {})
                        if isinstance(error_obj, dict):
                            error_message = error_obj.get('message', 'Unknown API error')
                        elif isinstance(error_obj, str):
                            error_message = error_obj
                        else:
                            error_message = str(error_obj) if error_obj else 'Unknown API error'
                        raise APIError(error_message, status_code=200)
                    
                    return json_response
                else:
                    return {"data": json_response}
            except ValueError as e:
                # If response is not JSON, return the text content wrapped in a dict
                return {"content": response.text, "parse_error": str(e)}
                
        except requests.exceptions.Timeout:
            raise FastRouterError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise FastRouterError("Failed to connect to FastRouter API")
        except requests.exceptions.RequestException as e:
            raise FastRouterError(f"Request failed: {str(e)}")
    
    def health(self) -> HealthResponse:
        """
        Check the health status of the FastRouter API
        
        Returns:
            Health status response
        """
        response_data = self._make_request("GET", "/health")
        return HealthResponse(response_data)
