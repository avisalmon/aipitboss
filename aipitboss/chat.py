"""
Chat module for AIPitBoss package.

This module provides a simplified interface for conversational AI interactions
using various AI services.
"""

from typing import Dict, Any, Optional, List, Union, Callable
import requests
from .ai_services import OpenAIService
from .anthropic_service import AnthropicService
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
            service: An initialized AI service (e.g., OpenAIService, AnthropicService)
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
        
        # Check service type and call appropriate method
        if isinstance(self.service, OpenAIService):
            response = self._ask_openai(model, temperature, max_tokens)
        elif isinstance(self.service, AnthropicService):
            response = self._ask_anthropic(model, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported service type: {type(self.service)}")
        
        # Add the assistant's response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def ask(self, question: str, **kwargs) -> str:
        """
        Alias for ask_question for simplified API.
        
        Args:
            question: The question to ask
            **kwargs: Optional arguments to pass to ask_question
            
        Returns:
            The AI's response as a string
        """
        return self.ask_question(question, **kwargs)
    
    def setService(self, service) -> None:
        """
        Change the service used by the chat instance.
        
        Args:
            service: An initialized AI service (e.g., OpenAIService, AnthropicService)
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
        
        # Check service type and call appropriate method
        if isinstance(self.service, OpenAIService):
            response = self._stream_openai(model, temperature, max_tokens, chunk_handler)
        elif isinstance(self.service, AnthropicService):
            # Most providers don't support streaming yet
            response = self._ask_anthropic(model, temperature, max_tokens)
            if chunk_handler:
                chunk_handler(response)
        else:
            raise ValueError(f"Unsupported service type: {type(self.service)}")
        
        # Add the assistant's response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _ask_openai(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 150
    ) -> str:
        """
        Ask a question using the OpenAI service.
        
        Args:
            model: Optional model to use (defaults to OpenAI's default)
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
        
        response = self.service.chat_completion(
            messages=self.conversation_history,
            **kwargs
        )
        
        return response["choices"][0]["message"]["content"]
    
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
    
    def _ask_anthropic(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 150
    ) -> str:
        """
        Ask a question using the Anthropic service.
        
        Args:
            model: Optional model to use (defaults to Anthropic's default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The AI's response as a string
        """
        # Format messages for Anthropic's API
        # Extract system message if present
        system_message = None
        messages = []
        
        for msg in self.conversation_history:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                messages.append(msg)
        
        kwargs = {
            "temperature": temperature,
        }
        
        if model:
            kwargs["model"] = model
            
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        
        response = self.service.message(
            messages=messages,
            system=system_message,
            **kwargs
        )
        
        return response["content"][0]["text"]
    
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