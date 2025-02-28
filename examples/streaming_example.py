"""
Example usage of streaming utilities from AIPitBoss package.

This script demonstrates how to use the StreamProcessor class
to handle streaming responses from AI APIs.
"""

import os
import time
import requests
from aipitboss import OpenAIService, AnthropicService, StreamProcessor


def openai_streaming_example():
    """
    Example of processing OpenAI streaming responses.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable")
        return
    
    # Create an OpenAI service instance
    openai = OpenAIService(api_key=api_key)
    
    # Prepare request data for streaming
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short poem about AI, one line at a time."}
        ],
        "temperature": 0.7,
        "stream": True  # Enable streaming
    }
    
    print("\nOpenAI Streaming Response:")
    print("---------------------------")
    
    try:
        # Make streaming request
        with requests.post(url, json=data, headers=headers, stream=True) as response:
            response.raise_for_status()
            
            # Process the stream
            StreamProcessor.process_openai_stream(
                response.iter_lines(),
                chunk_handler=StreamProcessor.print_stream
            )
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n---------------------------\n")


def anthropic_streaming_example():
    """
    Example of processing Anthropic streaming responses.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Please set the ANTHROPIC_API_KEY environment variable")
        return
    
    # Create an Anthropic service instance
    anthropic = AnthropicService(api_key=api_key)
    
    # Prepare request data for streaming
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    data = {
        "model": "claude-3-haiku-20240307",
        "messages": [
            {"role": "user", "content": "Count from 1 to 10, with a brief pause between each number."}
        ],
        "max_tokens": 100,
        "stream": True  # Enable streaming
    }
    
    print("Anthropic Streaming Response:")
    print("-----------------------------")
    
    try:
        # Make streaming request
        with requests.post(url, json=data, headers=headers, stream=True) as response:
            response.raise_for_status()
            
            # Define a custom handler that adds delays
            def delayed_handler(content):
                print(content, end="", flush=True)
                if content.strip() in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                    time.sleep(0.5)  # Add a delay after each number
            
            # Process the stream
            StreamProcessor.process_anthropic_stream(
                response.iter_lines(),
                chunk_handler=delayed_handler
            )
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n-----------------------------")


def main():
    """
    Main function demonstrating streaming utilities.
    """
    print("Streaming Examples\n")
    
    openai_streaming_example()
    anthropic_streaming_example()


if __name__ == "__main__":
    main() 