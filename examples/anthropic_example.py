"""
Example usage of the Anthropic service from AIPitBoss package.

This script demonstrates how to use the AnthropicService class
to interact with Anthropic's Claude models.
"""

import os
from aipitboss import AnthropicService


def main():
    """
    Main function demonstrating Anthropic service usage.
    """
    # Get API key from environment variable
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Please set the ANTHROPIC_API_KEY environment variable")
        return
    
    # Create an Anthropic service instance
    anthropic_service = AnthropicService(api_key=api_key)
    
    try:
        # Example message API (recommended for Claude 3 models)
        print("Making a request to Claude's message API...")
        
        # Format messages
        messages = anthropic_service.format_message_prompt(
            human_message="What are the key differences between Claude and GPT models?"
        )
        
        # Make the API call with a system prompt
        message_response = anthropic_service.message(
            messages=messages,
            model="claude-3-haiku-20240307",  # Using the smallest/fastest model
            max_tokens=500,
            temperature=0.7,
            system="You are a helpful, concise AI assistant specialized in explaining AI concepts."
        )
        
        # Print the response
        if "content" in message_response and len(message_response["content"]) > 0:
            message_text = message_response["content"][0]["text"]
            print(f"\nClaude's Response:\n{message_text}\n")
        else:
            print(f"\nUnexpected response format: {message_response}")
        
        # Example legacy completion API
        print("\nMaking a request to Claude's legacy completion API...")
        completion_response = anthropic_service.complete(
            prompt="What are three interesting applications of AI in healthcare?",
            model="claude-3-haiku-20240307",
            max_tokens_to_sample=500,
            temperature=0.7
        )
        
        # Print the completion
        if "completion" in completion_response:
            completion_text = completion_response["completion"]
            print(f"\nCompletion Response:\n{completion_text}\n")
        else:
            print(f"\nUnexpected response format: {completion_response}")
            
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main() 