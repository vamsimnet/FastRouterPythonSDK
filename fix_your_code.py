#!/usr/bin/env python3
"""
Quick fix for your streaming code

BEFORE (causes IndexError):
for chunk in completion:
    print(chunk.choices[0].delta)  # ❌ IndexError: list index out of range

AFTER (safe):
for chunk in completion:
    if chunk.choices and len(chunk.choices) > 0:  # ✅ Check if choices exist
        print(chunk.choices[0].delta)
"""

from fastrouter import FastRouter

def your_fixed_code():
    """Your exact code, but fixed"""
    
    client = FastRouter(api_key="sk-v1-your-api-key-here")

    completion = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[{"role": "user", "content": "Tell me about roger federer"}],
        max_tokens=20,
        stream=True,
        provider={"only": ["azure"]}
    )

    # ✅ FIXED VERSION - Check if choices exist before accessing
    for chunk in completion:
        if chunk.choices and len(chunk.choices) > 0:  # 🔧 Added safety check
            print(chunk.choices[0].delta)
            
    print("Streaming completed safely!")


def even_safer_version():
    """Even safer version with content checking"""
    
    client = FastRouter(api_key="sk-v1-your-api-key-here")

    completion = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[{"role": "user", "content": "Tell me about roger federer"}],
        max_tokens=20,
        stream=True,
        provider={"only": ["azure"]}
    )

    # ✅ SAFEST VERSION - Check everything before accessing
    for chunk in completion:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            
            # Print content as it streams
            if delta.content:
                print(delta.content, end='', flush=True)
            
            # Check for completion
            if chunk.choices[0].finish_reason:
                print(f"\n[DONE: {chunk.choices[0].finish_reason}]")
                break
    
    print("\nStreaming completed!")


def super_simple_version():
    """Super simple using convenience properties"""
    
    client = FastRouter(api_key="sk-v1-your-api-key-here")

    completion = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[{"role": "user", "content": "Tell me about roger federer"}],
        max_tokens=20,
        stream=True,
        provider={"only": ["azure"]}
    )

    # ✨ SIMPLEST VERSION - Using built-in safety
    for chunk in completion:
        if chunk.has_content:  # Built-in safety check
            print(chunk.content, end='', flush=True)  # Built-in safe content getter
    
    print("\nDone!")


if __name__ == "__main__":
    print("Choose the version you prefer:")
    print("1. your_fixed_code() - Your exact code but safe")
    print("2. even_safer_version() - More robust with content checking") 
    print("3. super_simple_version() - Using convenience properties")
    
    # Uncomment the one you want to test:
    # your_fixed_code()
    # even_safer_version()
    # super_simple_version()
