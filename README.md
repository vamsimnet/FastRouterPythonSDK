# FastRouter Python SDK

A Python client library for the FastRouter API, providing easy access to AI model completions with intelligent routing and provider selection.

## Installation

```bash
pip install fastrouter
```

Or install from source:

```bash
git clone https://github.com/vamsimnet/FastRouterPythonSDK.git
cd fastrouter-python
pip install -e .
```

## Quick Start

### Authentication

Set your API key as an environment variable:

```bash
export FASTROUTER_API_KEY="sk-v1-your-api-key-here"
```

Or pass it directly to the client:

```python
from fastrouter import FastRouter

client = FastRouter(api_key="sk-v1-your-api-key-here")
```

### Basic Usage

```python
from fastrouter import FastRouter

# Initialize the client
client = FastRouter()

# Create a chat completion
completion = client.chat.completions.create(
    model="openai/gpt-4.1",
    messages=[
        {
            "role": "user",
            "content": "What is Aqua?"
        }
    ],
    max_tokens=179,
    stream=False,
    provider={
        "only": ["azure"]
    }
)

# Access response using OpenAI-compatible attributes
print("Response:", completion.choices[0].message.content)
print("Model:", completion.model)
print("Usage:", completion.usage.total_tokens if completion.usage else "N/A")
```

### Health Check

```python
from fastrouter import FastRouter

client = FastRouter()

# Check API health
health_status = client.health()
print("Status:", health_status.status)
```

### Streaming Responses

FastRouter supports streaming responses for real-time chat completion:

```python
from fastrouter import FastRouter

client = FastRouter()

# Create streaming completion
completion = client.chat.completions.create(
    model="openai/gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Tell me a story"}],
    max_tokens=200,
    stream=True  # Enable streaming
)

# Iterate through streaming chunks - OpenAI compatible!
for chunk in completion:
    # Works exactly like OpenAI SDK (no IndexError handling needed)
    delta = chunk.choices[0].delta  
    if delta.content:
        print(delta.content, end='', flush=True)

# Alternative: Using convenience properties
for chunk in completion:
    if chunk.has_content:  # Built-in safety check
        print(chunk.content, end='', flush=True)  # Safe content getter
```

### Response Objects

The FastRouter SDK returns OpenAI-compatible response objects with attribute access:

```python
# OpenAI-style attribute access (recommended)
completion = client.chat.completions.create(...)
print(completion.choices[0].message.content)
print(completion.model)
print(completion.usage.total_tokens)

# Backward compatibility - dictionary access still works
response_dict = completion.to_dict()
print(response_dict['choices'][0]['message']['content'])
```

#### Response Object Types
- `ChatCompletion` - Main completion response (non-streaming)
- `StreamingChatCompletion` - Streaming completion response (iterable)
- `ChatCompletionChunk` - Individual chunk in streaming response
- `Choice` - Individual choice with message and finish reason  
- `ChoiceChunk` - Individual choice in streaming chunk
- `Message` - Message with role and content
- `Delta` - Delta object for streaming chunks (partial content)
- `Usage` - Token usage and cost information
- `HealthResponse` - Health check status

## API Reference

### FastRouter Client

#### `FastRouter(api_key=None, base_url="https://api.fastrouter.ai", timeout=30.0)`

Main client class for interacting with the FastRouter API.

**Parameters:**
- `api_key` (str, optional): Your FastRouter API key. If not provided, will read from `FASTROUTER_API_KEY` environment variable.
- `base_url` (str): Base URL for the FastRouter API. Default: "https://api.fastrouter.ai"
- `timeout` (float): Request timeout in seconds. Default: 30.0

### Chat Completions

#### `client.chat.completions.create(**kwargs)`

Create a chat completion request.

**Parameters:**
- `model` (str, required): The model to use (e.g., "openai/gpt-4.1")
- `messages` (List[Dict], required): List of message objects with "role" and "content"
- `max_tokens` (int, optional): Maximum number of tokens to generate
- `stream` (bool, optional): Whether to stream the response. Default: False
- `provider` (Dict, optional): Provider configuration (e.g., `{"only": ["azure"]}`)
- `temperature` (float, optional): Sampling temperature (0-2)
- `top_p` (float, optional): Nucleus sampling parameter (0-1)
- `frequency_penalty` (float, optional): Frequency penalty (-2 to 2)
- `presence_penalty` (float, optional): Presence penalty (-2 to 2)
- `stop` (str or List[str], optional): Stop sequences

**Example:**
```python
completion = client.chat.completions.create(
    model="openai/gpt-4.1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=100,
    temperature=0.7,
    provider={"only": ["openai"]}
)
```

### Health Check

#### `client.health()`

Check the health status of the FastRouter API.

**Returns:** Dictionary containing health status information.

## Error Handling

The SDK provides custom exception classes for different error scenarios:

```python
from fastrouter import FastRouter, APIError, AuthenticationError, FastRouterError

client = FastRouter()

try:
    completion = client.chat.completions.create(
        model="invalid-model",
        messages=[{"role": "user", "content": "Hello"}]
    )
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
except FastRouterError as e:
    print(f"General error: {e}")
```

## Examples

### Basic Chat Completion

```python
from fastrouter import FastRouter

client = FastRouter()

response = client.chat.completions.create(
    model="openai/gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    max_tokens=150
)

# OpenAI-compatible attribute access
print(response.choices[0].message.content)
```

### Using Specific Providers

```python
# Use only Azure OpenAI
response = client.chat.completions.create(
    model="openai/gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    provider={"only": ["azure"]}
)

# Exclude certain providers
response = client.chat.completions.create(
    model="openai/gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    provider={"exclude": ["aws"]}
)
```

### Advanced Parameters

```python
response = client.chat.completions.create(
    model="openai/gpt-4",
    messages=[
        {"role": "system", "content": "You are a creative writer."},
        {"role": "user", "content": "Write a short story about a robot"}
    ],
    max_tokens=500,
    temperature=0.8,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    stop=["THE END"]
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@fastrouter.ai or visit our [documentation](https://docs.fastrouter.ai/).
