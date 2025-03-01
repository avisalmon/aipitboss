#!/usr/bin/env python

"""
Enhanced Chat Example for AIPitBoss

This example demonstrates the enhanced features of the Chat class, including:
- Token tracking
- Conversation history management
- Switching between services
- Saving and loading chats
"""

import time
import os
from aipitboss.key_manager import KeyManager
from aipitboss.ai_service import AiService
from aipitboss.chat import Chat


def print_step(step_num, description):
    """Print a step in the process with formatting."""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*70}")


def print_messages(messages):
    """Print conversation messages with formatting."""
    for i, msg in enumerate(messages):
        role = msg["role"]
        content = msg["content"]
        # Truncate content if too long
        if len(content) > 100:
            content = content[:97] + "..."
        
        print(f"  Message {i+1}: [{role}] {content}")


def main():
    """Main function demonstrating enhanced Chat features."""
    print("\n" + "="*70)
    print("Enhanced Chat Example using AIPitBoss".center(70))
    print("="*70 + "\n")

    try:
        # Step 1: Initialize KeyManager
        print_step(1, "Initializing KeyManager")
        print("Loading API keys from environment variables or .keys.json file...")
        keys = KeyManager()
        print("✓ KeyManager initialized successfully")

        # Step 2: Get available services
        print_step(2, "Checking Available Services")
        services = keys.available_services()
        print(f"Available services: {', '.join(services.keys())}")
        
        # Choose OpenAI service first
        if "openai" not in services or not services["openai"].get("valid"):
            print("❌ OpenAI service is not available or invalid. Please check your API key.")
            return
            
        # Get available OpenAI models
        openai_models = services["openai"].get("models", [])
        if not openai_models:
            print("❌ No OpenAI models available.")
            return
            
        # Choose a suitable OpenAI model
        openai_model = None
        for model in openai_models:
            if "gpt" in model.lower():
                openai_model = model
                break
                
        if not openai_model:
            openai_model = openai_models[0]
            
        print(f"✓ Using OpenAI model: {openai_model}")
        
        # Check if Anthropic is available for later switching
        anthropic_available = "anthropic" in services and services["anthropic"].get("valid")
        anthropic_model = None
        
        if anthropic_available:
            anthropic_models = services["anthropic"].get("models", [])
            if anthropic_models:
                # Prefer Claude 3 models
                for model in anthropic_models:
                    if "claude-3" in model.lower():
                        anthropic_model = model
                        break
                        
                if not anthropic_model:
                    anthropic_model = anthropic_models[0]
                    
                print(f"✓ Anthropic service also available with model: {anthropic_model}")
            else:
                anthropic_available = False
                print("❌ No Anthropic models available.")
        else:
            print("❌ Anthropic service not available. Will only use OpenAI.")

        # Step 3: Initialize AiService with OpenAI
        print_step(3, "Creating OpenAI Service")
        print(f"Initializing AiService with OpenAI and model: {openai_model}")
        start_time = time.time()
        openai_service = AiService(keys, "openai", openai_model)
        print(f"✓ OpenAI service initialized in {time.time() - start_time:.2f} seconds")
        
        # Print service status
        status = openai_service.get_status()
        print("\nService Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Step 4: Create Chat instance
        print_step(4, "Creating Chat Instance")
        system_message = "You are a helpful, friendly, and concise assistant. Keep your answers brief but informative."
        print(f"System message: '{system_message}'")
        chat = Chat(openai_service, system_message)
        print("✓ Chat instance created successfully")

        # Step 5: Send initial questions
        print_step(5, "Sending Initial Questions")
        
        # First question
        question1 = "What are three interesting facts about the planet Mars?"
        print(f"\nQuestion 1: {question1}")
        print("Waiting for response...")
        start_time = time.time()
        response1 = chat.ask(question1, max_tokens=150)
        print(f"\nResponse received in {time.time() - start_time:.2f} seconds:")
        print(f"\n{response1}\n")
        
        # Get information about the request
        info = chat.last_as_info()
        print("\nLast Request Information:")
        print(f"  Time taken: {info['time_taken']:.2f} seconds")
        print(f"  Input tokens: {info['tokens_in']}")
        print(f"  Output tokens: {info['tokens_out']}")
        print(f"  Service: {info['service']}")
        print(f"  Model: {info['model']}")
        
        # Second question that builds on the first
        question2 = "How does Mars compare to Earth in terms of gravity and atmosphere?"
        print(f"\nQuestion 2: {question2}")
        print("Waiting for response...")
        start_time = time.time()
        response2 = chat.ask(question2, max_tokens=200)
        print(f"\nResponse received in {time.time() - start_time:.2f} seconds:")
        print(f"\n{response2}\n")
        
        # Step 6: Display conversation history
        print_step(6, "Conversation History")
        print("Current conversation history contains:")
        print_messages(chat.get_history())
        
        # Step 7: Save the conversation to a file
        print_step(7, "Saving Conversation")
        chat_file = "mars_chat.json"
        chat.save_chat(chat_file)
        print(f"Conversation saved to {chat_file}")
        
        # Step 8: Clear the history and start a new conversation
        print_step(8, "Clearing Conversation History")
        chat.clear_history()
        print("History cleared, but system message retained:")
        print_messages(chat.get_history())
        
        # New question after clearing history
        question3 = "What are the main challenges of sending humans to Mars?"
        print(f"\nNew question after clearing history: {question3}")
        print("Waiting for response...")
        response3 = chat.ask(question3, max_tokens=200)
        print(f"\nResponse: {response3}\n")
        
        # Step 9: Switch to Anthropic service if available
        if anthropic_available and anthropic_model:
            print_step(9, "Switching to Anthropic Service")
            print(f"Creating Anthropic service with model: {anthropic_model}")
            anthropic_service = AiService(keys, "anthropic", anthropic_model)
            
            # Replace the service in the chat
            chat.replace_service(anthropic_service)
            print("✓ Service replaced successfully")
            
            # Ask a question with the new service
            question4 = "How might the first human Mars colony be designed?"
            print(f"\nQuestion to Anthropic: {question4}")
            print("Waiting for response...")
            start_time = time.time()
            try:
                response4 = chat.ask(question4, max_tokens=300)
                print(f"\nResponse received in {time.time() - start_time:.2f} seconds:")
                print(f"\n{response4}\n")
                
                # Get information about the Anthropic request
                info = chat.last_as_info()
                print("\nAnthropic Request Information:")
                print(f"  Time taken: {info['time_taken']:.2f} seconds")
                print(f"  Service: {info['service']}")
                print(f"  Model: {info['model']}")
            except Exception as e:
                print(f"❌ Error when using Anthropic service: {e}")
                print("Reverting to OpenAI service")
                chat.replace_service(openai_service)
        
        # Step 10: Replace history with a summary
        print_step(10, "Replacing History with Summary")
        summary = "We've been discussing Mars exploration, including facts about Mars, comparison with Earth, and challenges of sending humans there."
        chat.replace_history(summary)
        print("History replaced with summary:")
        print_messages(chat.get_history())
        
        # Ask a final question based on the summary
        question5 = "What would be the most important scientific instruments to bring to Mars?"
        print(f"\nQuestion based on summary: {question5}")
        print("Waiting for response...")
        response5 = chat.ask(question5, max_tokens=250)
        print(f"\nResponse: {response5}\n")
        
        # Step 11: Load the previously saved conversation
        print_step(11, "Loading Previous Conversation")
        if os.path.exists(chat_file):
            new_chat = Chat(openai_service, "")  # Create a new empty chat
            new_chat.load_chat(chat_file, keys)
            print("Loaded conversation history:")
            print_messages(new_chat.get_history())
            
            # Continue the loaded conversation
            followup_question = "Could you elaborate more on the dust storms on Mars?"
            print(f"\nFollow-up question to loaded chat: {followup_question}")
            print("Waiting for response...")
            followup_response = new_chat.ask(followup_question, max_tokens=200)
            print(f"\nResponse: {followup_response}\n")
        else:
            print(f"Could not find saved chat file: {chat_file}")
        
        print("\n" + "="*70)
        print("Enhanced Chat Example Completed Successfully".center(70))
        print("="*70 + "\n")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 