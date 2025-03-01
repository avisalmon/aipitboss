"""
Chat module for AIPitBoss package.

This module provides a simplified interface for conversational AI interactions
using various AI services.
"""

from typing import Dict, Any, Optional, List, Union, Callable
import requests
from .ai_services import OpenAIService
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
        Initialize a Chat instance with an AI service.
        
        Args:
            service: An initialized AI service with a chat_completion method
            system_message: Default system message for chat interactions
        """
        self.service = service
        self.system_message = system_message
        self.conversation_history = []
        
        # Add default system message
        if system_message:
            self.conversation_history.append({
                "role": "system",
                "content": system_message
            })
    
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
            model: Optional model to use (defaults to service's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            clear_history: Whether to clear conversation history before asking
            
        Returns:
            The AI's response as a string
        """
        # Clear history if requested
        if clear_history:
            self.clear_history()
            # Re-add the system message
            if self.system_message:
                self.conversation_history.append({
                    "role": "system",
                    "content": self.system_message
                })
        
        # Add the user's question to history
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        
        # Get response from the service
        response = self._get_service_response(model, temperature, max_tokens)
        
        # Add the assistant's response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    # Proper method delegation for ask alias
    def ask(self, question: str, **kwargs) -> str:
        """
        Alias for ask_question method.
        
        Args:
            question: The question to ask
            **kwargs: Additional arguments to pass to ask_question
            
        Returns:
            The AI's response as a string
        """
        return self.ask_question(question, **kwargs)
    
    def setService(self, service) -> None:
        """
        Change the service used by the chat instance.
        
        Args:
            service: An initialized AI service with a chat_completion method
        """
        if not service:
            raise ValueError("Service cannot be None")
            
        # Update the service
        self.service = service
    
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
        Ask a question and stream the response from the AI service.
        
        Args:
            question: The question to ask
            model: Optional model to use (defaults to service's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            clear_history: Whether to clear conversation history before asking
            chunk_handler: Optional function to handle each chunk of the response
            
        Returns:
            The complete AI's response as a string
        """
        # Clear history if requested
        if clear_history:
            self.clear_history()
            # Re-add the system message
            if self.system_message:
                self.conversation_history.append({
                    "role": "system",
                    "content": self.system_message
                })
        
        # Add the user's question to history
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        
        # Check if we can use streaming with this service
        if isinstance(self.service, OpenAIService):
            response = self._stream_openai(model, temperature, max_tokens, chunk_handler)
        else:
            # Fallback to non-streaming for services that don't support it
            response = self._get_service_response(model, temperature, max_tokens)
            if chunk_handler:
                chunk_handler(response)
        
        # Add the assistant's response to history
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
        Get a response from the service.
        
        Args:
            model: Optional model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The AI's response as a string
        """
        kwargs = {
            "temperature": temperature,
        }
        
        if model:
            kwargs["model"] = model
            
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        # Call the service's chat_completion method
        response = self.service.chat_completion(
            messages=self.conversation_history,
            **kwargs
        )
        
        # Parse the response based on the service type
        # For OpenAI-style API
        if "choices" in response and len(response["choices"]) > 0:
            if "message" in response["choices"][0]:
                return response["choices"][0]["message"]["content"]
            elif "text" in response["choices"][0]:
                return response["choices"][0]["text"]
        
        # For content-style API (various providers)
        if "content" in response:
            if isinstance(response["content"], list) and len(response["content"]) > 0:
                if "text" in response["content"][0]:
                    return response["content"][0]["text"]
            elif isinstance(response["content"], str):
                return response["content"]
        
        # If we don't recognize the format, return the raw response
        return str(response)
    
    def _stream_openai(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
        chunk_handler: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Stream a response from OpenAI's API.
        
        Args:
            model: Optional model to use (defaults to OpenAI's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            chunk_handler: Optional function to handle each chunk of the response
            
        Returns:
            The complete AI's response as a string
        """
        # Use the default handler if none provided
        if chunk_handler is None:
            chunk_handler = StreamProcessor.print_stream
        
        # Extract necessary info from the service
        api_key = self.service.api.api_key
        base_url = self.service.api.base_url
        
        # Prepare the request data
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": self.conversation_history,
            "temperature": temperature,
            "stream": True  # Enable streaming
        }
        
        if model:
            data["model"] = model
            
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        # Make the streaming request
        response = requests.post(url, json=data, headers=headers, stream=True)
        response.raise_for_status()
        
        # Process the stream and return the full content
        return StreamProcessor.process_openai_stream(
            response.iter_lines(),
            chunk_handler=chunk_handler
        )
    
    def clear_history(self):
        """
        Clear the conversation history.
        """
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            The conversation history as a list of message dictionaries
        """
        return self.conversation_history 