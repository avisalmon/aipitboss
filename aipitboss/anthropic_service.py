"""
Anthropic Service module for AIPitBoss package.

This module provides a class for connecting to Anthropic's API
to interact with Claude models.
"""

from typing import Dict, Any, Optional, List, Union
from .api_connect import APIConnect
from .key_manager import KeyManager


class AnthropicService:
    """
    A class for interacting with Anthropic's API.
    
    This class provides simplified methods for using Anthropic's Claude models
    for message-based completions.
    """
    
    def __init__(
        self,
        service_name: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
        keys_file: Optional[str] = None,
        use_env: bool = True,
    ):
        """
        Initialize an Anthropic service.
        
        Args:
            service_name: Optional service name (e.g., "anthropic") for KeyManager lookup
            api_key: Anthropic API key (optional if using keys file or env vars)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            keys_file: Optional path to a JSON file containing API keys
            use_env: Whether to check environment variables for API keys
        """
        # Support simple initialization with just service name
        service = "anthropic"
        if service_name is not None:
            service = service_name
        
        # Get the API key using the KeyManager
        api_key = KeyManager.get_api_key(
            service=service,
            api_key=api_key,
            keys_file=keys_file,
            use_env=use_env,
        )
        
        # Set up headers with the Anthropic API key structure
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"  # API version
        }
            
        self.api = APIConnect(
            api_key=api_key,  # Not directly used in headers for Anthropic
            base_url="https://api.anthropic.com/v1",
            headers=headers,
            timeout=timeout
        )
        self.max_retries = max_retries
    
    def message(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a message completion with Anthropic's Claude API.
        
        Args:
            messages: List of message objects with role and content
            model: ID of the model to use (e.g., "claude-3-opus-20240229", "claude-3-sonnet-20240229")
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-1)
            system: Optional system prompt to instruct Claude
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        # Prepare the request data
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add optional system message
        if system:
            data["system"] = system
            
        # Add any additional parameters
        if kwargs:
            data.update(kwargs)
            
        return self.api.post("/messages", json_data=data)
    
    def complete(
        self,
        prompt: str,
        model: str = "claude-3-opus-20240229",
        max_tokens_to_sample: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a completion with Anthropic's Claude API (legacy endpoint).
        
        Args:
            prompt: The prompt to complete (should include "\n\nHuman: " and "\n\nAssistant: ")
            model: ID of the model to use
            max_tokens_to_sample: Maximum number of tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        # Ensure prompt has proper structure
        if not prompt.startswith("\n\nHuman: "):
            prompt = f"\n\nHuman: {prompt}"
        
        if "\n\nAssistant: " not in prompt:
            prompt = f"{prompt}\n\nAssistant: "
            
        # Prepare the request data
        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens_to_sample,
            "temperature": temperature
        }
            
        # Add any additional parameters
        if kwargs:
            data.update(kwargs)
            
        return self.api.post("/complete", json_data=data)
    
    def format_message_prompt(
        self,
        human_message: str,
        assistant_message: Optional[str] = None,
        system_message: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Format messages for the Claude message API.
        
        Args:
            human_message: The message from the human
            assistant_message: Optional message from the assistant (for continuing a conversation)
            system_message: Optional system message (for instructions)
            
        Returns:
            List of message dictionaries formatted for Claude
        """
        messages = []
        
        # Add the human message
        messages.append({
            "role": "user",
            "content": human_message
        })
        
        # Add assistant message if provided
        if assistant_message:
            messages.append({
                "role": "assistant",
                "content": assistant_message
            })
            
        return messages 