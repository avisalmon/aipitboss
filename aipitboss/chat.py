"""
Chat module for AIPitBoss package.

This module provides a simplified interface for conversational AI interactions
using various AI services.
"""

import json
import time
from typing import Dict, Any, Optional, List, Union, Callable
import requests
from .ai_service import AiService
from .streaming import StreamProcessor


class Chat:
    """
    A class that provides a simplified interface for chat interactions
    with different AI services.
    
    This class abstracts away the details of different AI service APIs
    and provides consistent methods for common operations like asking questions.
    """
    
    def __init__(
        self,
        service,
        system_message: str = "You are a helpful, concise assistant."
    ):
        """
        Initialize a chat instance with an AI service.
        
        Args:
            service: An AiService instance
            system_message: System message to set the behavior of the assistant
        """
        self.service = service
        self.system_message = system_message
        self.conversation_history = []
        
        # Add system message if provided
        if system_message:
            self.conversation_history.append({
                "role": "system",
                "content": system_message
            })
            
        # Track information about the last request
        self.last_request_info = {
            "time_taken": 0,
            "tokens_in": 0,
            "tokens_out": 0,
            "service": service.service_supplier,
            "model": service.model,
            "timestamp": None
        }
    
    def ask_question(
        self,
        question: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 150,
        clear_history: bool = False
    ) -> str:
        """
        Ask a question and get a response from the AI service.
        
        Args:
            question: The question to ask
            model: Optional model to use (overrides the service's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            clear_history: Whether to clear conversation history before asking
            
        Returns:
            The AI's response as a string
        """
        # Clear history if requested
        if clear_history:
            self.clear_history()
            
        # Add the user's question to the conversation
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        
        # Record the start time
        start_time = time.time()
        
        # Save initial token counts to calculate usage from this request
        initial_tokens_in = self.service.tokens_in
        initial_tokens_out = self.service.tokens_out
        
        # Get response
        kwargs = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = self._get_service_response(model, temperature, max_tokens)
        
        # Calculate time taken
        time_taken = time.time() - start_time
        
        # Calculate tokens used in this request
        tokens_in = self.service.tokens_in - initial_tokens_in
        tokens_out = self.service.tokens_out - initial_tokens_out
        
        # Update the last request info
        self.last_request_info = {
            "time_taken": time_taken,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "service": self.service.service_supplier,
            "model": self.service.model,
            "timestamp": time.time()
        }
        
        # Add the assistant's response to the conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
        
    def ask(self, question: str, **kwargs) -> str:
        """
        Simplified interface to ask a question.
        
        Args:
            question: The question to ask
            **kwargs: Additional parameters for ask_question
            
        Returns:
            The AI's response as a string
        """
        return self.ask_question(question, **kwargs)
        
    def replace_service(self, service) -> None:
        """
        Replace the current service with a new one.
        
        Args:
            service: The new AiService to use
        """
        self.service = service
        self.last_request_info["service"] = service.service_supplier
        self.last_request_info["model"] = service.model
        
    def stream_question(
        self,
        question: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
        clear_history: bool = False,
        chunk_handler: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Ask a question and stream the response.
        
        NOTE: This feature is partially implemented. Currently, it only works as a fallback 
        to non-streaming for most services. Full streaming is planned for a future release.
        
        Args:
            question: The question to ask
            model: Optional model to use (overrides the service's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            clear_history: Whether to clear conversation history before asking
            chunk_handler: Optional function to handle each chunk of content
            
        Returns:
            The complete response as a string
        """
        # Currently only implemented for specific services
        if self.service.service_supplier not in ["openai"]:
            print("Warning: Streaming is only supported for OpenAI services")
            print("Falling back to non-streaming request")
            return self.ask_question(
                question, model, temperature, max_tokens, clear_history
            )
        
        # Clear history if requested
        if clear_history:
            self.clear_history()
            
        # Add the user's question to the conversation
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        
        # Record start time for timing information
        start_time = time.time()
        
        # Save initial token counts to calculate usage from this request
        initial_tokens_in = self.service.tokens_in
        initial_tokens_out = self.service.tokens_out
        
        # Stream the response
        response = ""
        if self.service.service_supplier == "openai":
            response = self._stream_openai(model, temperature, max_tokens, chunk_handler)
        
        # Calculate time taken 
        time_taken = time.time() - start_time
        
        # Calculate tokens used in this request
        tokens_in = self.service.tokens_in - initial_tokens_in
        tokens_out = self.service.tokens_out - initial_tokens_out
        
        # Update the last request info
        self.last_request_info = {
            "time_taken": time_taken,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "service": self.service.service_supplier,
            "model": self.service.model,
            "timestamp": time.time()
        }
        
        # Add the assistant's response to the conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
            
    def _get_service_response(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 150
    ) -> str:
        """
        Get a response from the service and extract the message content.
        
        Args:
            model: Optional model to use (overrides the service's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            The AI's response as a string
        """
        # Check if the service is available
        if not self.service or not self.service.is_available():
            raise ValueError("No available service. Please initialize a valid service.")
            
        # Prepare keyword arguments
        kwargs = {}
        if model:
            kwargs["model"] = model
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
            
        # Make the API request
        response = self.service.chat_completion(
            messages=self.conversation_history,
            **kwargs
        )
        
        # Extract the response content based on the service
        content = ""
        if self.service.service_supplier == "openai":
            if "choices" in response and len(response["choices"]) > 0:
                if "message" in response["choices"][0]:
                    content = response["choices"][0]["message"]["content"]
                elif "text" in response["choices"][0]:
                    content = response["choices"][0]["text"]
        elif self.service.service_supplier == "anthropic":
            # Extract content from Anthropic response format
            if "content" in response:
                # Handle array of content blocks (newer Claude API versions)
                if isinstance(response["content"], list):
                    content_parts = []
                    for block in response["content"]:
                        if block.get("type") == "text":
                            content_parts.append(block.get("text", ""))
                    content = "".join(content_parts)
                else:
                    content = response["content"]
        else:
            # Generic approach for other services
            try:
                # First try to extract from a standard format
                if "choices" in response and len(response["choices"]) > 0:
                    if "message" in response["choices"][0]:
                        content = response["choices"][0]["message"]["content"]
                    elif "text" in response["choices"][0]:
                        content = response["choices"][0]["text"]
                # If that doesn't work, try alternate locations
                elif "content" in response:
                    content = response["content"]
                elif "output" in response:
                    content = response["output"]
                # If all else fails, use the entire response
                else:
                    content = str(response)
            except Exception as e:
                print(f"Warning: Error extracting content from response: {e}")
                content = str(response)
                
        return content
                
    def _stream_openai(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
        chunk_handler: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Stream a response from OpenAI.
        
        NOTE: This method is currently not implemented. The framework is in place
        for future development, but throws NotImplementedError when called.
        
        Args:
            model: Optional model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            chunk_handler: Optional function to handle each chunk
            
        Returns:
            The complete streamed response
        """
        # TODO: Implement streaming for OpenAI in a future release
        raise NotImplementedError("Streaming not yet implemented")
    
    def clear_history(self):
        """
        Clear the conversation history, keeping only the system message if one exists.
        """
        system_message = None
        # Preserve the system message if it exists
        for message in self.conversation_history:
            if message["role"] == "system":
                system_message = message
                break
                
        # Clear the history
        self.conversation_history = []
        
        # Add back the system message if one was found
        if system_message:
            self.conversation_history.append(system_message)
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history

    def replace_history(self, new_text: str) -> None:
        """
        Replace the conversation history with a new text.
        This is useful for summarizing or compressing long conversations.
        
        Args:
            new_text: The new conversation history as a text string
        """
        # Keep the system message if one exists
        system_message = None
        for message in self.conversation_history:
            if message["role"] == "system":
                system_message = message
                break
        
        # Create a new history with the provided text
        self.conversation_history = []
        
        # Add back the system message if one was found
        if system_message:
            self.conversation_history.append(system_message)
            
        # Add the new text as a user message
        self.conversation_history.append({
            "role": "user",
            "content": new_text
        })

    def last_as_info(self) -> Dict[str, Any]:
        """
        Get information about the last request.
        
        Returns:
            Dictionary with information about the last request
        """
        return self.last_request_info
        
    def save_chat(self, file_path: str) -> None:
        """
        Save the chat history and settings to a file.
        
        Args:
            file_path: Path to the file where chat should be saved
        """
        # Create a dictionary with all the chat information
        chat_data = {
            "conversation_history": self.conversation_history,
            "system_message": self.system_message,
            "service_info": {
                "supplier": self.service.service_supplier,
                "model": self.service.model
            },
            "last_request_info": self.last_request_info
        }
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
            
        print(f"Chat saved to {file_path}")
        
    def load_chat(self, file_path: str, key_manager=None) -> None:
        """
        Load a chat from a file.
        
        Args:
            file_path: Path to the chat file
            key_manager: Optional KeyManager instance to create new service
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
                
            # Load conversation history
            if "conversation_history" in chat_data:
                self.conversation_history = chat_data["conversation_history"]
                
            # Load system message
            if "system_message" in chat_data:
                self.system_message = chat_data["system_message"]
                
            # Load service information if key_manager is provided
            if key_manager and "service_info" in chat_data:
                service_info = chat_data["service_info"]
                try:
                    # Try to create a new service with the same supplier and model
                    new_service = AiService(
                        key_manager,
                        service_info["supplier"],
                        service_info["model"]
                    )
                    self.service = new_service
                except Exception as e:
                    print(f"Warning: Could not create new service - {e}")
                    print("Keeping the current service.")
                    
            # Load last request info
            if "last_request_info" in chat_data:
                self.last_request_info = chat_data["last_request_info"]
                
            print(f"Chat loaded from {file_path}")
            
        except Exception as e:
            raise Exception(f"Error loading chat from {file_path}: {e}") 