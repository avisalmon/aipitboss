#!/usr/bin/env python
"""
Anthropic Chat Example for AIPitBoss

This example demonstrates how to use the AiService and Chat classes
to interact with Anthropic's Claude API. It includes progress reporting
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
    """Main function demonstrating Anthropic chat usage."""
    print("\n" + "="*70)
    print("Anthropic Chat Example using AIPitBoss".center(70))
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
        
        # Check if Anthropic is available
        if "anthropic" not in services or not services["anthropic"].get("valid"):
            print("❌ Anthropic service is not available or invalid. Please check your API key.")
            print("Make sure you have an Anthropic API key set in ANTHROPIC_API_KEY environment variable")
            print("or in your .keys.json file.")
            return
        
        # Show available Anthropic models
        anthropic_models = services["anthropic"].get("models", [])
        if anthropic_models:
            print(f"Available Anthropic models: {', '.join(anthropic_models)}")
            
            # Note: model IDs can change over time as Claude evolves
            # Find modern claude-3 models, preferring -7 series, then -5 series in descending order
            # This helps ensure we get the newest available model based on naming patterns
            preferred_models = [
                "claude-3-7", # 3.7 series (newest)
                "claude-3-5", # 3.5 series
                "claude-3"    # Standard claude-3 series
            ]
            
            found_model = False
            for preferred in preferred_models:
                if any(m.startswith(preferred) for m in anthropic_models):
                    matching = [m for m in anthropic_models if m.startswith(preferred)]
                    # Sort to get latest/newest first based on model ID
                    matching.sort(reverse=True)
                    model = matching[0]
                    print(f"✓ Using {model} model")
                    found_model = True
                    break
            
            if not found_model:
                # If no preferred model found, use the first available model
                print(f"✓ Using {anthropic_models[0]} model")
                model = anthropic_models[0]
        else:
            print("No Anthropic models found. Using default model: claude-3-5-sonnet-20241022")
            model = "claude-3-5-sonnet-20241022"  # Default to a more recent model

        # Step 3: Initialize AiService
        print_step(3, "Creating Anthropic Service")
        print(f"Initializing AiService with Anthropic and model: {model}")
        start_time = time.time()
        ai_service = AiService(keys, "anthropic", model)
        print(f"✓ AiService initialized in {time.time() - start_time:.2f} seconds")
        
        # Print service status
        status = ai_service.get_status()
        print("\nService Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Step 4: Create Chat instance
        print_step(4, "Creating Chat Instance")
        system_message = "You are Claude, a helpful and accurate AI assistant. Please provide concise responses."
        print(f"System message: '{system_message}'")
        chat = Chat(ai_service, system_message)
        print("✓ Chat instance created successfully")

        # Step 5: Ask questions
        print_step(5, "Sending Chat Messages")
        
        # First question
        question1 = "What are the key differences between Claude and other AI assistants?"
        print(f"\nQuestion 1: {question1}")
        print("Waiting for response...")
        start_time = time.time()
        response1 = chat.ask(question1, max_tokens=300)
        print(f"\nResponse received in {time.time() - start_time:.2f} seconds:")
        print(f"\n{response1}\n")
        
        # Check token usage after first question
        print("\nToken Usage After Question 1:")
        print(f"  Input tokens: {ai_service.tokens_in}")
        print(f"  Output tokens: {ai_service.tokens_out}")
        print(f"  Total tokens: {ai_service.tokens_in + ai_service.tokens_out}")
        print(f"  Remaining budget: {ai_service.token_budget}")
        
        # Second question - follow-up
        question2 = "Can you explain more about Anthropic's Constitutional AI approach?"
        print(f"\nQuestion 2: {question2}")
        print("Waiting for response...")
        start_time = time.time()
        response2 = chat.ask(question2, max_tokens=400)
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
        print("Anthropic Chat Example Completed Successfully".center(70))
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        
        # For Anthropic API errors, provide more helpful information
        if "401" in str(e) and "anthropic" in str(e).lower():
            print("\nTIP: For 401 Unauthorized errors with Anthropic API:")
            print("  - Make sure your API key starts with 'sk-ant-'")
            print("  - Check that your API key is valid and not expired")
            print("  - Ensure you have proper authentication headers set")


if __name__ == "__main__":
    main() 