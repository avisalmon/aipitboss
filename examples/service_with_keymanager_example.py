#!/usr/bin/env python
"""
Example demonstrating how to use AIPitBoss services with the KeyManager.

This script shows how to initialize and use AI services with different
key management strategies.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path to import the local version of the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aipitboss import (
    OpenAIService,
    AnthropicService,
    HuggingFaceService,
    KeyManager
)

# Helper function to print section headers
def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "-"))
    print("=" * 60 + "\n")

# -------------------- OpenAI Example --------------------
print_header("OpenAI Service with KeyManager")

# Create an OpenAI service using different key methods
print("Initializing OpenAI service...")

# Try to initialize with highest priority: direct key, then file, then env
try:
    openai = OpenAIService(
        api_key=None,  # Try this first
        keys_file=".keys.json",  # Then try this
        use_env=True  # Finally try environment variable
    )
    
    # Test if the service has a valid API key
    # Note: We're not actually making an API call here
    if openai.api_key:
        print("✓ OpenAI service initialized successfully")
    else:
        print("✗ No API key found for OpenAI")
except Exception as e:
    print(f"Error initializing OpenAI service: {e}")

# -------------------- Anthropic Example --------------------
print_header("Anthropic Service with KeyManager")

# Create an Anthropic service with key management
print("Initializing Anthropic service...")

try:
    anthropic = AnthropicService(
        api_key=None,
        keys_file=".keys.json",
        use_env=True
    )
    
    # Check if API key is available
    if anthropic.api_key:
        print("✓ Anthropic service initialized successfully")
    else:
        print("✗ No API key found for Anthropic")
except Exception as e:
    print(f"Error initializing Anthropic service: {e}")

# -------------------- Hugging Face Example --------------------
print_header("Hugging Face Service with KeyManager")

# Create a Hugging Face service with key management
print("Initializing Hugging Face service...")

try:
    huggingface = HuggingFaceService(
        api_key=None,
        keys_file=".keys.json",
        use_env=True
    )
    
    # Check if API key is available
    if huggingface.api_key:
        print("✓ Hugging Face service initialized successfully")
    else:
        print("✗ No API key found for Hugging Face")
except Exception as e:
    print(f"Error initializing Hugging Face service: {e}")

# -------------------- Making API Calls --------------------
print_header("Making API Calls")

print("To make API calls with the initialized services:")
print("""
# OpenAI example
if openai.api_key:
    response = openai.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, who are you?"}
        ],
        model="gpt-3.5-turbo"
    )
    print(response["choices"][0]["message"]["content"])

# Anthropic example
if anthropic.api_key:
    response = anthropic.message(
        messages=[{
            "role": "user",
            "content": "Hello, who are you?"
        }],
        model="claude-3-haiku-20240307",
        max_tokens=100
    )
    print(response["content"][0]["text"])

# Hugging Face example
if huggingface.api_key:
    response = huggingface.text_generation(
        model="gpt2",
        prompt="Once upon a time"
    )
    print(response)
""")

# -------------------- Key Status --------------------
print_header("API Key Status")

# Check what keys are available
def check_key_source(service_name):
    """Check and report where the API key for a service comes from."""
    # Check environment variable
    env_var_name = f"{service_name.upper()}_API_KEY"
    env_key = os.environ.get(env_var_name)
    
    # Check keys file
    keys_file = Path(".keys.json")
    file_key = None
    if keys_file.exists():
        try:
            with open(keys_file, 'r') as f:
                keys = json.load(f)
                file_key = keys.get(service_name.lower())
        except:
            pass
    
    # Report findings
    sources = []
    if env_key:
        sources.append(f"Environment variable ({env_var_name})")
    if file_key:
        sources.append("Keys file (.keys.json)")
    
    if sources:
        print(f"{service_name}: Available from {' and '.join(sources)}")
    else:
        print(f"{service_name}: No API key found")

# Check key sources for each service
check_key_source("OPENAI")
check_key_source("ANTHROPIC")
check_key_source("HUGGINGFACE")

# -------------------- Setup Instructions --------------------
print_header("Setting Up API Keys")

print("To set up your API keys, run the setup script:")
print("\n    python setup_keys.py\n")
print("Or manually create a .keys.json file with:")
print("""{
    "openai": "your-openai-api-key",
    "anthropic": "your-anthropic-api-key",
    "huggingface": "your-huggingface-api-key"
}""")
print("\nYou can also set environment variables:")
print("    OPENAI_API_KEY, ANTHROPIC_API_KEY, HUGGINGFACE_API_KEY") 