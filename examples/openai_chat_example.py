#!/usr/bin/env python
"""
OpenAI Chat Example for AIPitBoss

This example demonstrates how to use the AiService and Chat classes
to interact with OpenAI's chat API. It includes progress reporting
and token usage tracking.
"""

import time
import sys
from aipitboss.key_manager import KeyManager
from aipitboss.ai_service import AiService
from aipitboss.chat import Chat


def print_step(step_num, description):
    """Print a step in the process with formatting."""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*70}")
    time.sleep(0.5)  # Small delay for readability


def main():
    """Main function demonstrating OpenAI chat usage."""
    print("\n" + "="*70)
    print("OpenAI Chat Example using AIPitBoss".center(70))
    print("="*70 + "\n")

    try:
        # Step 1: Initialize KeyManager
        print_step(1, "Initializing KeyManager")
        print("Loading API keys from environment variables or .keys.json file...")
        keys = KeyManager()
        print("✓ KeyManager initialized successfully")

        # Step 2: Check available services
        print_step(2, "Checking Available Services")
        services = keys.available_services()
        print(f"Available services: {', '.join(services.keys())}")
        
        # Check if OpenAI is available
        if "openai" not in services or not services["openai"].get("valid"):
            print("❌ OpenAI service is not available or invalid. Please check your API key.")
            return
        
        # Show available OpenAI models
        openai_models = services["openai"].get("models", [])
        if openai_models:
            print(f"Available OpenAI models: {', '.join(openai_models[:5])}...")
            if "gpt-3.5-turbo" in openai_models:
                print("✓ Using gpt-3.5-turbo model")
                model = "gpt-3.5-turbo"
            else:
                print(f"✓ Using {openai_models[0]} model")
                model = openai_models[0]
        else:
            print("✓ Using default model: gpt-3.5-turbo")
            model = "gpt-3.5-turbo"

        # Step 3: Initialize AiService
        print_step(3, "Creating OpenAI Service")
        print(f"Initializing AiService with OpenAI and model: {model}")
        start_time = time.time()
        ai_service = AiService(keys, "openai", model)
        print(f"✓ AiService initialized in {time.time() - start_time:.2f} seconds")
        
        # Print service status
        status = ai_service.get_status()
        print("\nService Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Step 4: Create Chat instance
        print_step(4, "Creating Chat Instance")
        system_message = "You are a helpful, concise assistant that provides accurate and brief answers."
        print(f"System message: '{system_message}'")
        chat = Chat(ai_service, system_message)
        print("✓ Chat instance created successfully")

        # Step 5: Ask questions
        print_step(5, "Sending Chat Messages")
        
        # First question
        question1 = "What are the top 3 benefits of Python for data science?"
        print(f"\nQuestion 1: {question1}")
        print("Waiting for response...")
        start_time = time.time()
        response1 = chat.ask(question1)
        print(f"\nResponse received in {time.time() - start_time:.2f} seconds:")
        print(f"\n{response1}\n")
        
        # Check token usage after first question
        print("\nToken Usage After Question 1:")
        print(f"  Input tokens: {ai_service.tokens_in}")
        print(f"  Output tokens: {ai_service.tokens_out}")
        print(f"  Total tokens: {ai_service.tokens_in + ai_service.tokens_out}")
        print(f"  Remaining budget: {ai_service.token_budget}")
        
        # Second question - follow-up
        question2 = "Can you recommend 2 Python libraries for each of those benefits?"
        print(f"\nQuestion 2: {question2}")
        print("Waiting for response...")
        start_time = time.time()
        response2 = chat.ask(question2)
        print(f"\nResponse received in {time.time() - start_time:.2f} seconds:")
        print(f"\n{response2}\n")
        
        # Check token usage after second question
        print("\nToken Usage After Question 2:")
        print(f"  Input tokens: {ai_service.tokens_in}")
        print(f"  Output tokens: {ai_service.tokens_out}")
        print(f"  Total tokens: {ai_service.tokens_in + ai_service.tokens_out}")
        print(f"  Remaining budget: {ai_service.token_budget}")
        
        # Step 6: Demonstrate conversation history
        print_step(6, "Conversation History")
        print("Current conversation history contains:")
        for i, message in enumerate(chat.conversation_history):
            print(f"  Message {i+1}: [{message['role']}] {message['content'][:50]}...")

        print("\n" + "="*70)
        print("OpenAI Chat Example Completed Successfully".center(70))
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 