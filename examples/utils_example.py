"""
Example usage of utility functions from AIPitBoss package.

This script demonstrates how to use the utility functions
provided in the AIPitBoss package.
"""

import time
import random
from aipitboss.utils import retry, format_prompt, parse_json_response, extract_text_from_response


def main():
    """
    Main function demonstrating utility functions.
    """
    # Example of format_prompt
    print("Example of format_prompt:")
    template = "Hello, {name}! Welcome to {service}."
    formatted = format_prompt(template, name="Alice", service="AIPitBoss")
    print(formatted)
    print()
    
    # Example of parse_json_response
    print("Example of parse_json_response:")
    valid_json = '{"name": "Alice", "age": 30, "interests": ["AI", "Python"]}'
    invalid_json = '{name: "Alice", broken json'
    
    parsed_valid = parse_json_response(valid_json)
    parsed_invalid = parse_json_response(invalid_json, default={"error": "Invalid JSON"})
    
    print(f"Valid JSON parsed: {parsed_valid}")
    print(f"Invalid JSON with default: {parsed_invalid}")
    print()
    
    # Example of extract_text_from_response
    print("Example of extract_text_from_response:")
    response = {
        "id": "chat_123",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Paris is the capital of France."
                }
            }
        ]
    }
    
    text = extract_text_from_response(response, "choices.0.message.content")
    print(f"Extracted text: {text}")
    
    # Try a path that doesn't exist
    missing_text = extract_text_from_response(response, "invalid.path", default="Not found")
    print(f"Missing path with default: {missing_text}")
    print()
    
    # Example of retry
    print("Example of retry function:")
    
    # Define a function that fails sometimes
    def unreliable_function():
        """A function that fails randomly to demonstrate retry."""
        if random.random() < 0.7:  # 70% chance of failing
            print("  Function failed, will retry...")
            raise ConnectionError("Random failure")
        print("  Function succeeded!")
        return "Success result"
    
    # Use retry to make it more reliable
    try:
        result = retry(
            unreliable_function,
            max_retries=3,
            retry_delay=0.5,
            backoff_factor=2.0,
            errors_to_retry=(ConnectionError,)
        )
        print(f"Final result: {result}")
    except Exception as e:
        print(f"Retry eventually failed: {e}")


if __name__ == "__main__":
    main() 