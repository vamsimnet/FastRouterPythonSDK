"""FastRouter client implementation"""

import json
import requests
from typing import Dict, List, Optional, Any, Union
from .exceptions import FastRouterError, APIError, AuthenticationError
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
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to FastRouter API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request payload for POST/PUT requests
            params: Query parameters
            
        Returns:
            Response JSON data
            
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
                timeout=self.timeout
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_message = error_data.get('error', {}).get('message', 'Unknown API error')
                    else:
                        error_message = str(error_data)
                except (ValueError, KeyError):
                    error_message = f"HTTP {response.status_code}: {response.text}"
                raise APIError(error_message, status_code=response.status_code)
            
            # Try to parse JSON response
            try:
                json_response = response.json()
                # Ensure we always return a dictionary
                if isinstance(json_response, dict):
                    return json_response
                else:
                    return {"data": json_response}
            except ValueError:
                # If response is not JSON, return the text content wrapped in a dict
                return {"content": response.text}
                
        except requests.exceptions.Timeout:
            raise FastRouterError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise FastRouterError("Failed to connect to FastRouter API")
        except requests.exceptions.RequestException as e:
            raise FastRouterError(f"Request failed: {str(e)}")
    
    def health(self) -> Dict[str, Any]:
        """
        Check the health status of the FastRouter API
        
        Returns:
            Health status response
        """
        return self._make_request("GET", "/health")
