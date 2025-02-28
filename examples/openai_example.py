"""
Example usage of the OpenAI service from AIPitBoss package.

This script demonstrates how to use the OpenAIService class
to interact with OpenAI's API.
"""

import os
from aipitboss import OpenAIService


def main():
    """
    Main function demonstrating OpenAI service usage.
    """
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Please set the OPENAI_API_KEY environment variable")
        return
    
    # Create an OpenAI service instance
    openai_service = OpenAIService(api_key=api_key)
    
    try:
        # Example chat completion
        print("Making chat completion request...")
        chat_response = openai_service.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What are the benefits of using Python for data science?"}
            ],
            model="gpt-3.5-turbo"
        )
        
        # Print the response
        if "choices" in chat_response and len(chat_response["choices"]) > 0:
            message = chat_response["choices"][0]["message"]["content"]
            print(f"\nChat Response:\n{message}\n")
        else:
            print(f"\nUnexpected response format: {chat_response}")
        
        # Example image generation
        print("\nMaking image generation request...")
        image_response = openai_service.image_generation(
            prompt="A beautiful sunset over mountains",
            size="512x512",
            n=1
        )
        
        # Print the image URL
        if "data" in image_response and len(image_response["data"]) > 0:
            image_url = image_response["data"][0]["url"]
            print(f"\nGenerated Image URL: {image_url}\n")
        else:
            print(f"\nUnexpected response format: {image_response}")
            
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main() 