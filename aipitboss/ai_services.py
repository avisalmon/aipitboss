"""
AI Services module for AIPitBoss package.

This module provides specialized classes for connecting to
popular AI service APIs like OpenAI, Hugging Face, etc.
"""

from typing import Dict, Any, Optional, List, Union
from .api_connect import APIConnect
from .key_manager import KeyManager
import json
from pathlib import Path


class OpenAIService:
    """
    A class for interacting with OpenAI's API.
    
    This class provides simplified methods for common OpenAI API operations
    like generating text completions, creating chat completions, and
    generating images.
    """
    
    def __init__(
        self,
        service_name: Optional[str] = None,
        api_key: Optional[str] = None,
        organization_id: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
        keys_file: Optional[str] = None,
        use_env: bool = True,
    ):
        """
        Initialize an OpenAI service.
        
        Args:
            service_name: Optional service name (e.g., "openai") for KeyManager lookup
            api_key: OpenAI API key (optional if using keys file or env vars)
            organization_id: Optional OpenAI organization ID
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            keys_file: Optional path to a JSON file containing API keys
            use_env: Whether to check environment variables for API keys
        """
        # Support simple initialization with just service name
        self.service_name = "openai"
        if service_name is not None:
            self.service_name = service_name
        
        self.organization_id = organization_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.keys_file = keys_file
        self.use_env = use_env
        
        # Try to find keys file in current directory or parent directory
        if self.keys_file is None:
            from pathlib import Path
            current_dir_keys = ".keys.json"
            parent_dir_keys = "../.keys.json"
            
            if Path(current_dir_keys).exists():
                self.keys_file = current_dir_keys
            elif Path(parent_dir_keys).exists():
                self.keys_file = parent_dir_keys
        
        # Get the API key using the KeyManager
        try:
            api_key = KeyManager.get_api_key(
                service=self.service_name,
                api_key=api_key,
                keys_file=self.keys_file,
                use_env=self.use_env,
            )
            
            headers = {}
            if self.organization_id:
                headers["OpenAI-Organization"] = self.organization_id
                
            self.api = APIConnect(
                api_key=api_key,
                base_url="https://api.openai.com/v1",
                headers=headers,
                timeout=self.timeout
            )
        except ValueError as e:
            print(f"Error initializing OpenAIService: {e}")
            self.api = None
    
    def get_services(self) -> List[str]:
        """
        Get a list of available service names from the keys file.
        
        Returns:
            List of service names with API keys in the keys file
        """
        services = []
        
        # Check if keys file exists
        if self.keys_file and Path(self.keys_file).exists():
            try:
                with open(self.keys_file, 'r') as f:
                    keys = json.load(f)
                services = list(keys.keys())
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return services
    
    def set_service(self, service: str) -> bool:
        """
        Change the service provider.
        
        Args:
            service: Name of the service to use (must be in keys file)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.keys_file or not Path(self.keys_file).exists():
            print(f"No keys file found.")
            return False
            
        try:
            # Check if the service exists in the keys file
            services = self.get_services()
            if service not in services:
                print(f"Service '{service}' not found in keys file.")
                return False
                
            # Update the service name
            self.service_name = service
            
            # Get the new API key
            api_key = KeyManager.get_api_key(
                service=service,
                keys_file=self.keys_file,
                use_env=self.use_env,
            )
            
            # Update the API connection
            headers = {}
            if self.organization_id:
                headers["OpenAI-Organization"] = self.organization_id
                
            self.api = APIConnect(
                api_key=api_key,
                base_url="https://api.openai.com/v1",
                headers=headers,
                timeout=self.timeout
            )
            
            return True
        except ValueError as e:
            print(f"Error setting service: {e}")
            return False
            
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion with the OpenAI API.
        
        Args:
            messages: List of message objects with role and content
            model: ID of the model to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
            
        if kwargs:
            data.update(kwargs)
            
        return self.api.post("/chat/completions", json_data=data)
    
    def text_completion(
        self,
        prompt: str,
        model: str = "text-davinci-003",
        temperature: float = 0.7,
        max_tokens: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a text completion with the OpenAI API.
        
        Args:
            prompt: Text prompt to complete
            model: ID of the model to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if kwargs:
            data.update(kwargs)
            
        return self.api.post("/completions", json_data=data)
    
    def image_generation(
        self,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate images with the OpenAI API.
        
        Args:
            prompt: Text description of the desired image
            size: Size of the generated images
            n: Number of images to generate
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        data = {
            "prompt": prompt,
            "size": size,
            "n": n
        }
        
        if kwargs:
            data.update(kwargs)
            
        return self.api.post("/images/generations", json_data=data)


class HuggingFaceService:
    """
    A class for interacting with Hugging Face's API.
    
    This class provides simplified methods for common Hugging Face API
    operations like inference with different models.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        keys_file: Optional[str] = None,
        use_env: bool = True,
    ):
        """
        Initialize a Hugging Face service.
        
        Args:
            api_key: Hugging Face API key (optional if using keys file or env vars)
            timeout: Request timeout in seconds
            keys_file: Optional path to a JSON file containing API keys
            use_env: Whether to check environment variables for API keys
        """
        # Get the API key using the KeyManager
        api_key = KeyManager.get_api_key(
            service="huggingface",
            api_key=api_key,
            keys_file=keys_file,
            use_env=use_env,
        )
        
        self.api = APIConnect(
            api_key=api_key,
            base_url="https://api-inference.huggingface.co/models",
            timeout=timeout
        )
    
    def inference(
        self,
        model: str,
        inputs: Union[str, Dict[str, Any], List[Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run inference with a Hugging Face model.
        
        Args:
            model: Model ID (e.g., "gpt2", "facebook/bart-large-cnn")
            inputs: Input data for the model
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        data = {"inputs": inputs}
        
        if kwargs:
            data.update(kwargs)
            
        return self.api.post(f"/{model}", json_data=data)
    
    def text_generation(
        self,
        model: str,
        prompt: str,
        max_length: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text with a Hugging Face model.
        
        Args:
            model: Model ID (e.g., "gpt2", "EleutherAI/gpt-neo-1.3B")
            prompt: Text prompt to complete
            max_length: Maximum length of generated text
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        data = {"inputs": prompt}
        
        if max_length is not None:
            data["parameters"] = data.get("parameters", {})
            data["parameters"]["max_length"] = max_length
            
        if kwargs:
            parameters = kwargs.pop("parameters", {})
            if parameters:
                data["parameters"] = data.get("parameters", {})
                data["parameters"].update(parameters)
            data.update(kwargs)
            
        return self.api.post(f"/{model}", json_data=data)
    
    def image_classification(
        self,
        model: str,
        image_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Classify an image with a Hugging Face model.
        
        Args:
            model: Model ID (e.g., "google/vit-base-patch16-224")
            image_url: URL of the image to classify
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            API response as a dictionary
        """
        data = {"inputs": image_url}
        
        if kwargs:
            data.update(kwargs)
            
        return self.api.post(f"/{model}", json_data=data) 