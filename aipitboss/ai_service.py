"""
AI Service module for AIPitBoss package.

This module provides a generic service class for interacting with various AI service providers,
including token tracking and budget management.
"""

from typing import Dict, Any, Optional, List, Union
from .key_manager import KeyManager
import json


class AiService:
    """
    A generic class for AI services across different providers.
    
    This class provides a unified interface for AI services with features like:
    - Service and model validation against KeyManager
    - Token usage tracking
    - Budget management to limit API usage
    """
    
    def __init__(
        self,
        keys: KeyManager,
        service_supplier: str,
        model: str,
    ):
        """
        Initialize an AI service.
        
        Args:
            keys: KeyManager instance with API keys
            service_supplier: Service provider name (e.g., "openai", "anthropic")
            model: Model name to use (must be available in the service)
            
        Returns:
            True if initialization successful, False otherwise
        """
        self.keys = keys
        self.service_supplier = service_supplier
        self.model = model
        
        # Token tracking attributes
        self.tokens_in = 0
        self.tokens_out = 0
        self.token_budget = 1000000
        self.hold = False
        
        # Initialize success flag
        self.initialized = False
        
        # Set base_url based on service_supplier
        self.base_url = self._get_base_url()
        
        # Validate service and model
        if not self._validate_service_and_model():
            return
            
        # Mark as successfully initialized
        self.initialized = True
        
    def _get_base_url(self) -> str:
        """
        Get the base URL for the API based on service supplier.
        
        Returns:
            Base URL string
        """
        if self.service_supplier == "openai":
            return "https://api.openai.com/v1"
        elif self.service_supplier == "anthropic":
            return "https://api.anthropic.com/v1"
        else:
            # Default to empty string, will be configured during validation if needed
            return ""
    
    def _validate_service_and_model(self) -> bool:
        """
        Validate that the service supplier and model are available.
        
        Returns:
            True if valid, False otherwise
        """
        # Check available services
        services = self.keys.available_services()
        
        # Check if service exists
        if self.service_supplier not in services:
            print(f"Service '{self.service_supplier}' not found in available services")
            return False
            
        # Check if service is valid
        service_info = services[self.service_supplier]
        if not service_info.get('valid'):
            print(f"Service '{self.service_supplier}' has an invalid API key")
            return False
            
        # Check if model exists for this service
        models = service_info.get('models', [])
        if models and self.model not in models:
            print(f"Model '{self.model}' not found in available models for '{self.service_supplier}'")
            return False
            
        # Get the API key
        try:
            self.api_key = self.keys.get_api_key(self.service_supplier)
        except ValueError as e:
            print(f"Error retrieving API key: {e}")
            return False
            
        return True
    
    def add_tokens_in(self, num: int) -> None:
        """
        Add to the input token count and update budget.
        
        Args:
            num: Number of tokens to add
        """
        self.tokens_in += num
        self._update_budget()
        
    def add_tokens_out(self, num: int) -> None:
        """
        Add to the output token count and update budget.
        
        Args:
            num: Number of tokens to add
        """
        self.tokens_out += num
        self._update_budget()
        
    def _update_budget(self) -> None:
        """
        Update the token budget and hold status.
        """
        # Calculate total token usage
        total_usage = self.tokens_in + self.tokens_out
        
        # Update budget
        self.token_budget = max(0, 1000000 - total_usage)
        
        # Update hold status if budget is depleted
        if self.token_budget == 0 and not self.hold:
            self.hold = True
            print(f"Budget depleted for service '{self.service_supplier}' with model '{self.model}'. Service on hold.")
            
    def bump_budget(self, num: int = 1000000) -> None:
        """
        Increase the token budget and reset hold status.
        
        Args:
            num: Amount to add to the budget (default: 1000000)
        """
        self.token_budget += num
        self.hold = False
        print(f"Budget increased by {num} tokens. Service '{self.service_supplier}' is active again.")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the service.
        
        Returns:
            Dictionary with service status information
        """
        return {
            "service": self.service_supplier,
            "model": self.model,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "token_budget": self.token_budget,
            "on_hold": self.hold,
            "initialized": self.initialized
        }
    
    def is_available(self) -> bool:
        """
        Check if the service is available for use.
        
        Returns:
            True if service is initialized and not on hold
        """
        return self.initialized and not self.hold 
        
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion with the AI service.
        
        Args:
            messages: List of message objects with role and content
            model: ID of the model to use (defaults to initialized model)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        if not self.is_available():
            raise ValueError(f"Service '{self.service_supplier}' is not available. Check initialization or budget.")
            
        # Use the model we initialized with if not specified
        model_to_use = model if model else self.model
        
        # Validate inputs
        if not messages or not isinstance(messages, list):
            raise ValueError("Messages must be a non-empty list of message objects")
        
        # Ensure each message has the correct format
        for message in messages:
            if not isinstance(message, dict):
                raise ValueError(f"Message must be a dictionary, got {type(message)}")
            if "role" not in message:
                raise ValueError(f"Message missing 'role' field: {message}")
            if "content" not in message:
                raise ValueError(f"Message missing 'content' field: {message}")
        
        # Prepare request data
        data = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
            
        if kwargs:
            data.update(kwargs)
        
        # Determine the endpoint based on the service
        endpoint = "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Apply service-specific adjustments
        if self.service_supplier == "anthropic":
            # For Anthropic, use Claude Messages API
            endpoint = "/messages"
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            # Anthropic requires different data structure
            # Extract system message if present
            system_message = None
            user_assistant_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    # Convert from OpenAI format to Anthropic format
                    # Map "user" -> "user", "assistant" -> "assistant"
                    if msg["role"] in ["user", "assistant"]:
                        user_assistant_messages.append(msg)
            
            # Construct Anthropic-specific request
            data = {
                "model": model_to_use,
                "messages": user_assistant_messages,
                "max_tokens": max_tokens if max_tokens else 1000,
                "temperature": temperature
            }
            
            # Add system message if we found one
            if system_message:
                data["system"] = system_message
        elif self.service_supplier == "openai":
            # Ensure the messages are properly formatted for OpenAI
            # Validate each message has a valid role
            for message in messages:
                if message["role"] not in ["system", "user", "assistant", "function", "tool"]:
                    raise ValueError(f"Invalid role '{message['role']}' for OpenAI. Must be one of: system, user, assistant, function, tool")
        elif self.service_supplier != "openai":
            # Add more services as needed
            raise ValueError(f"Service '{self.service_supplier}' is not supported for chat completions.")
        
        # Make the request
        import requests
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Debug
            if self.service_supplier == "anthropic":
                print(f"Making Anthropic API request to: {url}")
                print(f"With model: {model_to_use}")
                print(f"Request payload: {json.dumps(data)[:200]}...")
                
            response = requests.post(url, json=data, headers=headers)
            
            # Debug
            if self.service_supplier == "anthropic":
                print(f"Response status code: {response.status_code}")
                print(f"Response content: {response.text[:200]}...")
            
            # Check for HTTP errors
            if response.status_code != 200:
                err_msg = f"API request failed with status code {response.status_code}"
                err_details = ""
                
                # Try to get more details from the response
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        err_details = str(error_data["error"])
                    else:
                        err_details = str(error_data)
                except:
                    err_details = response.text[:200]
                
                # Handle common error codes
                if response.status_code == 404:
                    raise ValueError(f"Not found: The requested resource or endpoint does not exist. Check if the model '{model_to_use}' exists.")
            
            # For other status codes, raise the standard exception
            response.raise_for_status()
            
            result = response.json()
            
            # Update token usage if available in response
            if "usage" in result:
                usage = result["usage"]
                if "prompt_tokens" in usage:
                    self.add_tokens_in(usage["prompt_tokens"])
                if "completion_tokens" in usage:
                    self.add_tokens_out(usage["completion_tokens"])
            
            return result
        except requests.exceptions.RequestException as e:
            # More detailed error handling for request exceptions
            error_msg = f"Request to {self.service_supplier} API failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if "error" in error_data:
                        error_msg += f"\nAPI Error: {error_data['error'].get('message', str(error_data['error']))}"
                except:
                    error_msg += f"\nStatus code: {e.response.status_code}, Content: {e.response.text[:200]}"
            raise Exception(error_msg)
        except ValueError as e:
            # Re-raise ValueError with the same message
            raise
        except Exception as e:
            # Generic error with context
            error_details = f"Service: {self.service_supplier}, Model: {model_to_use}, URL: {url}"
            error_data = f"Request data: {data}"
            raise Exception(f"Error in chat completion: {str(e)}\n{error_details}\n{error_data}") 