"""
FastRouter Python SDK - Usage Examples

This file demonstrates various ways to use the FastRouter Python SDK.
Make sure to set your FASTROUTER_API_KEY environment variable or pass it directly to the client.
"""

import os
from fastrouter import FastRouter, APIError, AuthenticationError, FastRouterError


def basic_completion_example():
    """Basic chat completion example"""
    print("=== Basic Chat Completion ===")
    
    client = FastRouter()
    
    try:
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
        
        # New OpenAI-compatible attribute access
        print("Message content:", completion.choices[0].message.content)
        print("Model used:", completion.model)  
        print("Usage tokens:", completion.usage.total_tokens if completion.usage else "N/A")
        
        # Backward compatibility - dictionary access still works
        print("Full response type:", type(completion))
        
    except Exception as e:
        print(f"Error: {e}")


def advanced_completion_example():
    """Advanced chat completion with multiple parameters"""
    print("\n=== Advanced Chat Completion ===")
    
    client = FastRouter()
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that explains complex topics simply."
                },
                {
                    "role": "user",
                    "content": "Explain quantum computing in 2-3 sentences."
                }
            ],
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            stop=["Note:"]
        )
        
        # Show both attribute and dictionary access
        print("Content (attribute):", completion.choices[0].message.content)
        print("Finish reason:", completion.choices[0].finish_reason)
        print("Provider used:", completion.usage.provider if completion.usage else "N/A")
        
    except Exception as e:
        print(f"Error: {e}")


def health_check_example():
    """Health check example"""
    print("\n=== Health Check ===")
    
    client = FastRouter()
    
    try:
        health = client.health()
        print("Health status:", health.status)
        print("Health response type:", type(health))
        
    except Exception as e:
        print(f"Error: {e}")


def error_handling_example():
    """Demonstrate error handling"""
    print("\n=== Error Handling ===")
    
    # Example with invalid API key
    client = FastRouter(api_key="invalid-key")
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-4",
            messages=[{"role": "user", "content": "Hello"}]
        )
    except AuthenticationError:
        print("✓ Caught AuthenticationError for invalid API key")
    except APIError as e:
        print(f"✓ Caught APIError: {e} (Status: {e.status_code})")
    except FastRouterError as e:
        print(f"✓ Caught FastRouterError: {e}")


def provider_selection_example():
    """Demonstrate provider selection"""
    print("\n=== Provider Selection ===")
    
    client = FastRouter()
    
    try:
        # Only use Azure
        print("Using only Azure:")
        completion1 = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello from Azure!"}],
            provider={"only": ["azure"]},
            max_tokens=50
        )
        print("Azure response received")
        
        # Exclude AWS
        print("\nExcluding AWS:")
        completion2 = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello without AWS!"}],
            provider={"exclude": ["aws"]},
            max_tokens=50
        )
        print("Non-AWS response received")
        
    except Exception as e:
        print(f"Error: {e}")


def streaming_example():
    """Demonstrate streaming chat completion"""
    print("\n=== Streaming Chat Completion ===")
    
    client = FastRouter()
    
    try:
        print("Creating streaming completion...")
        completion = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Tell me a short story about a robot, streaming word by word"}
            ],
            max_tokens=100,
            stream=True,
            temperature=0.7
        )
        
        print("Streaming response:")
        full_content = ""
        
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                print(content, end='', flush=True)  # Print without newline
        
        print(f"\n\nFull response length: {len(full_content)} characters")
        
    except Exception as e:
        print(f"Error in streaming: {e}")


def conversation_example():
    """Demonstrate a multi-turn conversation"""
    print("\n=== Multi-turn Conversation ===")
    
    client = FastRouter()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    
    conversation_turns = [
        "Hello, what's your name?",
        "Can you help me with Python programming?",
        "What's the difference between lists and tuples?"
    ]
    
    for user_input in conversation_turns:
        messages.append({"role": "user", "content": user_input})
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            # Extract assistant's response - now using attribute access!
            assistant_message = completion.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_message})
            
            print(f"User: {user_input}")
            print(f"Assistant: {assistant_message}\n")
            
        except Exception as e:
            print(f"Error in conversation: {e}")
            break


def main():
    """Run all examples"""
    print("FastRouter Python SDK Examples")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('FASTROUTER_API_KEY')
    if not api_key:
        print("⚠️  Warning: FASTROUTER_API_KEY environment variable not set")
        print("   Some examples may fail. Set your API key with:")
        print("   export FASTROUTER_API_KEY='sk-v1-your-api-key-here'")
        print()
    
    # Run examples
    basic_completion_example()
    advanced_completion_example()
    health_check_example()
    error_handling_example()
    provider_selection_example()
    streaming_example()
    conversation_example()


if __name__ == "__main__":
    main()
