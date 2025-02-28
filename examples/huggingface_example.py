"""
Example usage of the Hugging Face service from AIPitBoss package.

This script demonstrates how to use the HuggingFaceService class
to interact with Hugging Face's API.
"""

import os
from aipitboss import HuggingFaceService


def main():
    """
    Main function demonstrating Hugging Face service usage.
    """
    # Get API key from environment variable
    api_key = os.getenv("HF_API_KEY")
    
    if not api_key:
        print("Please set the HF_API_KEY environment variable")
        return
    
    # Create a Hugging Face service instance
    hf_service = HuggingFaceService(api_key=api_key)
    
    try:
        # Example text generation
        print("Making text generation request...")
        text_response = hf_service.text_generation(
            model="gpt2",
            prompt="Once upon a time,",
            max_length=50
        )
        
        # Print the response
        print(f"\nText Generation Response:\n{text_response}\n")
        
        # Example image classification
        print("\nMaking image classification request...")
        image_response = hf_service.image_classification(
            model="google/vit-base-patch16-224",
            image_url="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/pipeline-cat-chonk.jpeg"
        )
        
        # Print the classifications
        print(f"\nImage Classification Response:\n{image_response}\n")
            
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main() 