"""
Simple tests for FastRouter Python SDK

Run with: python test_fastrouter.py
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import fastrouter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastrouter import FastRouter, APIError, AuthenticationError, FastRouterError


class TestFastRouter(unittest.TestCase):
    """Test cases for FastRouter client"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = FastRouter(api_key="test-key", base_url="https://api.test.com")
    
    def test_client_initialization(self):
        """Test client initialization"""
        client = FastRouter(api_key="test-key")
        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.base_url, "https://api.fastrouter.ai")
        self.assertEqual(client.timeout, 30.0)
        
        # Test with custom parameters
        client2 = FastRouter(
            api_key="test-key2",
            base_url="https://custom.api.com",
            timeout=60.0
        )
        self.assertEqual(client2.api_key, "test-key2")
        self.assertEqual(client2.base_url, "https://custom.api.com")
        self.assertEqual(client2.timeout, 60.0)
    
    def test_headers_generation(self):
        """Test header generation"""
        headers = self.client._get_headers()
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(headers['Authorization'], 'Bearer test-key')
    
    @patch('requests.request')
    def test_successful_request(self, mock_request):
        """Test successful API request"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response
        
        result = self.client._make_request("GET", "/test")
        
        self.assertEqual(result, {"status": "success"})
        mock_request.assert_called_once()
    
    @patch('requests.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling"""
        # Mock 401 response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        with self.assertRaises(AuthenticationError):
            self.client._make_request("GET", "/test")
    
    @patch('requests.request')
    def test_api_error(self, mock_request):
        """Test API error handling"""
        # Mock 400 response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Bad request"}
        }
        mock_request.return_value = mock_response
        
        with self.assertRaises(APIError) as context:
            self.client._make_request("GET", "/test")
        
        self.assertEqual(context.exception.status_code, 400)
    
    @patch('requests.request')
    def test_health_check(self, mock_request):
        """Test health check endpoint"""
        # Mock successful health response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_request.return_value = mock_response
        
        result = self.client.health()
        
        self.assertEqual(result, {"status": "healthy"})
        mock_request.assert_called_with(
            method="GET",
            url="https://api.test.com/health",
            headers=self.client._get_headers(),
            json=None,
            params=None,
            timeout=self.client.timeout
        )
    
    @patch('requests.request')
    def test_chat_completion(self, mock_request):
        """Test chat completion creation"""
        # Mock successful completion response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    }
                }
            ]
        }
        mock_request.return_value = mock_response
        
        result = self.client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=50
        )
        
        self.assertIn("choices", result)
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]["method"], "POST")
        self.assertEqual(call_args[1]["url"], "https://api.test.com/api/v1/chat/completions")
        
        # Check the payload
        expected_payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
            "max_tokens": 50
        }
        self.assertEqual(call_args[1]["json"], expected_payload)
    
    def test_environment_api_key(self):
        """Test API key from environment variable"""
        with patch.dict(os.environ, {'FASTROUTER_API_KEY': 'env-key'}):
            client = FastRouter()
            self.assertEqual(client.api_key, 'env-key')


class TestChatCompletions(unittest.TestCase):
    """Test cases for chat completions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = FastRouter(api_key="test-key")
    
    def test_completions_creation_with_all_params(self):
        """Test completion creation with all parameters"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"test": "response"}
            
            result = self.client.chat.completions.create(
                model="openai/gpt-4",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=100,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stop=["STOP"],
                stream=True,
                provider={"only": ["azure"]}
            )
            
            # Verify the request was made with correct parameters
            mock_request.assert_called_once_with(
                method="POST",
                endpoint="/api/v1/chat/completions",
                data={
                    "model": "openai/gpt-4",
                    "messages": [{"role": "user", "content": "Test"}],
                    "stream": True,
                    "max_tokens": 100,
                    "provider": {"only": ["azure"]},
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1,
                    "stop": ["STOP"]
                }
            )


def run_integration_tests():
    """Run integration tests with real API (optional)"""
    print("\n" + "="*50)
    print("INTEGRATION TESTS")
    print("="*50)
    
    api_key = os.getenv('FASTROUTER_API_KEY')
    if not api_key:
        print("⚠️  Skipping integration tests - FASTROUTER_API_KEY not set")
        return
    
    print("🔑 API key found - running integration tests...")
    
    try:
        client = FastRouter()
        
        # Test health check
        print("Testing health endpoint...")
        health = client.health()
        print(f"✅ Health check passed: {health}")
        
        # Test chat completion
        print("Testing chat completion...")
        completion = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print(f"✅ Chat completion passed")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")


if __name__ == '__main__':
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests if API key is available
    run_integration_tests()
