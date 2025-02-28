#!/usr/bin/env python
"""
Example demonstrating how to use AIPitBoss's key management system.

This script shows different ways to provide API keys to AIPitBoss services.
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path to import the local version of the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aipitboss import OpenAIService, AnthropicService, HuggingFaceService, KeyManager

def print_separator(title):
    """Print a section separator with a title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "-"))
    print("=" * 50 + "\n")


# Example 1: Using direct API key
print_separator("Example 1: Direct API Key")
print("# This approach requires providing the API key directly in code")
print("# Not recommended for production or shared code\n")
print("openai = OpenAIService(api_key='your-openai-api-key-here')")
print("response = openai.chat_completion(...)")


# Example 2: Using environment variables
print_separator("Example 2: Environment Variables")
print("# Set environment variables before running your script")
print("# Environment variables used: OPENAI_API_KEY, ANTHROPIC_API_KEY, HUGGINGFACE_API_KEY\n")
print("openai = OpenAIService(use_env=True)")
print("anthropic = AnthropicService(use_env=True)")
print("huggingface = HuggingFaceService(use_env=True)")

# Check if any environment variables are set
env_keys = {
    "OpenAI": os.environ.get("OPENAI_API_KEY"),
    "Anthropic": os.environ.get("ANTHROPIC_API_KEY"),
    "HuggingFace": os.environ.get("HUGGINGFACE_API_KEY")
}

print("\nCurrent environment variables status:")
for service, key in env_keys.items():
    status = "Set" if key else "Not set"
    print(f"{service} API key: {status}")


# Example 3: Using a keys file
print_separator("Example 3: Keys File")
print("# Store your API keys in a .keys.json file")
print("# This file should be in .gitignore to prevent committing secrets\n")
print("openai = OpenAIService(keys_file='.keys.json')")
print("anthropic = AnthropicService(keys_file='.keys.json')")
print("huggingface = HuggingFaceService(keys_file='.keys.json')")

# Check if keys file exists
keys_file = Path(".keys.json")
if keys_file.exists():
    try:
        with open(keys_file, 'r') as f:
            keys = json.load(f)
        print("\nKeys file found with the following services:")
        for service in keys:
            print(f"- {service}")
    except Exception as e:
        print(f"\nError reading keys file: {e}")
else:
    print("\nNo .keys.json file found in the current directory.")
    print("To create one, run: python setup_keys.py")


# Example 4: Priority order
print_separator("Example 4: Priority Order")
print("# When multiple sources are available, AIPitBoss uses the following priority:")
print("# 1. Direct API key (if provided)")
print("# 2. Keys file (if found)")
print("# 3. Environment variable (if set)")
print("\nExample with all options:")
print("openai = OpenAIService(")
print("    api_key='optional-direct-key',  # Highest priority")
print("    keys_file='.keys.json',        # Second priority")
print("    use_env=True                   # Lowest priority")
print(")")


# Example 5: Using KeyManager directly
print_separator("Example 5: Using KeyManager Directly")
print("# You can use the KeyManager class directly for more control\n")
print("from aipitboss import KeyManager")
print("")
print("# Get API key with fallback options")
print("api_key = KeyManager.get_api_key(")
print("    service='openai',")
print("    api_key=None,")
print("    keys_file='.keys.json',")
print("    use_env=True")
print(")")
print("")
print("# Save API keys to a file")
print("KeyManager.save_keys(")
print("    {")
print("        'openai': 'your-openai-key',")
print("        'anthropic': 'your-anthropic-key',")
print("        'huggingface': 'your-huggingface-key'")
print("    },")
print("    keys_file='.keys.json'")
print(")")


# Conclusion
print_separator("Conclusion")
print("For more information on AIPitBoss's key management system, see:")
print("- README.md documentation")
print("- setup_keys.py script")
print("- aipitboss/key_manager.py source code") 