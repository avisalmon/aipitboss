#!/usr/bin/env python
"""
Setup script for AIPitBoss API keys.

This script helps users set up their API keys for AIPitBoss.
It prompts for API keys and saves them to a .keys.json file.
"""

import os
import json
import getpass
from pathlib import Path

# Try to import from the installed package, fall back to local import
try:
    from aipitboss.key_manager import KeyManager
except ImportError:
    # For development, when running from the source tree
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from aipitboss.key_manager import KeyManager


def setup_keys():
    """
    Set up API keys for AIPitBoss.
    """
    print("AIPitBoss API Key Setup")
    print("===================")
    print("\nThis script will help you set up your API keys for AIPitBoss.")
    print("You can leave any field blank if you don't have that API key.")
    print("Keys will be saved to .keys.json in the current directory.")
    print("\nPress Ctrl+C at any time to exit without saving.\n")
    
    # Dictionary to store the keys
    keys = {}
    
    # Ask for OpenAI API key
    openai_key = getpass.getpass("OpenAI API Key (hidden input): ").strip()
    if openai_key:
        keys["openai"] = openai_key
    
    # Ask for Anthropic API key
    anthropic_key = getpass.getpass("Anthropic API Key (hidden input): ").strip()
    if anthropic_key:
        keys["anthropic"] = anthropic_key
    
    # Ask for HuggingFace API key
    huggingface_key = getpass.getpass("HuggingFace API Key (hidden input): ").strip()
    if huggingface_key:
        keys["huggingface"] = huggingface_key
    
    # Save keys if any were provided
    if keys:
        # Default to .keys.json in the current directory
        keys_file = ".keys.json"
        
        # Save the keys
        KeyManager.save_keys(keys, keys_file)
        
        print(f"\nAPI keys saved to {os.path.abspath(keys_file)}")
        print("You can now use AIPitBoss with these API keys.")
    else:
        print("\nNo API keys were provided. Nothing was saved.")


if __name__ == "__main__":
    try:
        setup_keys()
    except KeyboardInterrupt:
        print("\n\nSetup canceled. No keys were saved.")
    except Exception as e:
        print(f"\nError during setup: {e}") 