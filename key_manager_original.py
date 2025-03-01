"""
Key Management module for AIPitBoss package.

This module provides utilities for loading and managing API keys
from different sources (environment variables, key files, or direct input).
It also validates keys and tracks available services and models.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Optional, Any, Union, List, Tuple, Set


class KeyManager:
    """
    A class to manage API keys for different services.
    
    This class provides methods to load API keys from environment variables,
    from a key file, or directly from parameters. It also validates keys
    and tracks which services and models are available.
    """
    
    # Default keys file location (in user's home directory)
    DEFAULT_KEYS_FILE = os.path.join(str(Path.home()), ".aipitboss_keys.json")
    
    # Default keys file in the current directory
    LOCAL_KEYS_FILE = os.path.join(os.getcwd(), ".keys.json")
    
    # Environment variable prefixes for different services
    ENV_PREFIXES = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "huggingface": "HF_API_KEY",
    }
    
    # Base URLs for service API testing
    BASE_URLS = {
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com",
        "huggingface": "https://api-inference.huggingface.co/models",
    }
    
    # Endpoints to test API keys
    TEST_ENDPOINTS = {
        "openai": "/models",
        "anthropic": "/v1/models",
        "huggingface": "",  # Will be set per model
    }
    
    def __init__(
        self,
        keys_file: Optional[str] = None,
        use_env: bool = True,
        validate_keys: bool = True
    ):
        """
        Initialize the KeyManager.
        
        This will:
        1. Check environment variables for API keys
        2. Check keys file for API keys
        3. Validate keys and identify available services and models
        
        Args:
            keys_file: Optional path to a keys file
            use_env: Whether to check environment variables
            validate_keys: Whether to validate keys by making test requests
        """
        self.keys_file = keys_file or self.LOCAL_KEYS_FILE
        self.use_env = use_env
        
        # Find keys file in current or parent directory if not specified
        if self.keys_file == self.LOCAL_KEYS_FILE and not Path(self.keys_file).exists():
            parent_dir_keys = os.path.join(os.path.dirname(os.getcwd()), ".keys.json")
            if Path(parent_dir_keys).exists():
                self.keys_file = parent_dir_keys
        
        # Dictionary to store information about each service
        self.services_info = {}
        
        # Load all available keys
        self._load_all_keys()
        
        # Validate keys if requested
        if validate_keys:
            self._validate_keys()
    
    def _load_all_keys(self) -> None:
        """
        Load all available keys from environment variables and keys file.
        """
        # First check environment variables
        if self.use_env:
            for service, env_var in self.ENV_PREFIXES.items():
                key = os.environ.get(env_var)
                if key:
                    if service not in self.services_info:
                        self.services_info[service] = {
                            "api_key": key,
                            "source": "environment",
                            "valid": None,  # Will be set during validation
                            "models": []    # Will be populated during validation
                        }
        
        # Then check keys file
        if self.keys_file and Path(self.keys_file).exists():
            try:
                with open(self.keys_file, 'r') as f:
                    keys = json.load(f)
                
                # Add keys from file if not already loaded from environment
                for service, key in keys.items():
                    # Skip non-key entries (like comments)
                    if service.startswith("_") or service == "comment":
                        continue
                        
                    if service not in self.services_info and key:
                        self.services_info[service] = {
                            "api_key": key,
                            "source": "file",
                            "valid": None,  # Will be set during validation
                            "models": []    # Will be populated during validation
                        }
            except (json.JSONDecodeError, FileNotFoundError):
                pass
    
    def _validate_keys(self) -> None:
        """
        Validate API keys by making test requests and update services_info.
        """
        for service, info in self.services_info.items():
            # Skip if service is not supported for validation
            if service not in self.BASE_URLS or service not in self.TEST_ENDPOINTS:
                info["valid"] = None
                continue
                
            # Prepare request
            base_url = self.BASE_URLS[service]
            endpoint = self.TEST_ENDPOINTS[service]
            headers = {"Authorization": f"Bearer {info['api_key']}"}
            
            # Different services might have different auth methods
            if service == "anthropic":
                headers = {
                    "x-api-key": info['api_key'],
                    "anthropic-version": "2023-06-01"
                }
            
            try:
                # Make a test request to validate the key
                response = requests.get(
                    f"{base_url}{endpoint}",
                    headers=headers,
                    timeout=5
                )
                
                # Check if request was successful
                if response.status_code == 200:
                    info["valid"] = True
                    
                    # Extract available models if possible
                    try:
                        data = response.json()
                        if service == "openai" and "data" in data:
                            # OpenAI models data structure
                            info["models"] = [model["id"] for model in data["data"]]
                        elif service == "anthropic" and "models" in data:
                            # Anthropic models data structure
                            info["models"] = data["models"]
                    except Exception:
                        # If we can't parse models, that's okay
                        pass
                else:
                    info["valid"] = False
            except Exception:
                # Request failed, key is probably invalid
                info["valid"] = False
    
    def get_api_key(self, service: str) -> str:
        """
        Get the API key for a specific service.
        
        Args:
            service: Service name (e.g., "openai", "anthropic")
            
        Returns:
            API key for the service
            
        Raises:
            ValueError: If no API key is found for the service
        """
        if service in self.services_info:
            return self.services_info[service]["api_key"]
        
        # Try the older static method as fallback for any other sources
        # This is for backwards compatibility
        try:
            return KeyManager._get_api_key_static(
                service=service,
                api_key=None,
                keys_file=self.keys_file,
                use_env=self.use_env
            )
        except ValueError:
            pass
            
        raise ValueError(
            f"API key for {service} not found. Please provide it directly, "
            f"in a keys file, or set the {self.ENV_PREFIXES.get(service, service.upper() + '_API_KEY')} "
            "environment variable."
        )
    
    def add_key(self, service: str, key: str, env: bool = False) -> bool:
        """
        Add a new API key for a service.
        
        Args:
            service: Service name (e.g., "openai", "anthropic")
            key: API key for the service
            env: Whether to save as environment variable (otherwise to file)
            
        Returns:
            True if successful, False otherwise
        """
        if not key:
            return False
            
        # Set as environment variable if requested
        if env:
            env_var = self.ENV_PREFIXES.get(service, f"{service.upper()}_API_KEY")
            os.environ[env_var] = key
            
            # Update our services info
            self.services_info[service] = {
                "api_key": key,
                "source": "environment",
                "valid": None,  # Not validated yet
                "models": []    # Not populated yet
            }
            
            # Validate the new key
            self._validate_service_key(service)
            return True
        
        # Otherwise save to file
        if not self.keys_file:
            self.keys_file = self.LOCAL_KEYS_FILE
            
        # Load existing keys
        existing_keys = {}
        if Path(self.keys_file).exists():
            try:
                with open(self.keys_file, 'r') as f:
                    existing_keys = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Update with new key
        existing_keys[service] = key
        
        # Create directory if needed
        directory = os.path.dirname(self.keys_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Save back to file
        try:
            with open(self.keys_file, 'w') as f:
                json.dump(existing_keys, f, indent=2)
                
            # Update our services info
            self.services_info[service] = {
                "api_key": key,
                "source": "file",
                "valid": None,  # Not validated yet
                "models": []    # Not populated yet
            }
            
            # Validate the new key
            self._validate_service_key(service)
            return True
        except Exception:
            return False
    
    def _validate_service_key(self, service: str) -> None:
        """
        Validate a specific service key.
        
        Args:
            service: Service name to validate
        """
        if service not in self.services_info:
            return
            
        info = self.services_info[service]
        
        # Skip if service is not supported for validation
        if service not in self.BASE_URLS or service not in self.TEST_ENDPOINTS:
            info["valid"] = None
            return
            
        # Prepare request
        base_url = self.BASE_URLS[service]
        endpoint = self.TEST_ENDPOINTS[service]
        headers = {"Authorization": f"Bearer {info['api_key']}"}
        
        # Different services might have different auth methods
        if service == "anthropic":
            headers = {
                "x-api-key": info['api_key'],
                "anthropic-version": "2023-06-01"
            }
        
        try:
            # Make a test request to validate the key
            response = requests.get(
                f"{base_url}{endpoint}",
                headers=headers,
                timeout=5
            )
            
            # Check if request was successful
            if response.status_code == 200:
                info["valid"] = True
                
                # Extract available models if possible
                try:
                    data = response.json()
                    if service == "openai" and "data" in data:
                        # OpenAI models data structure
                        info["models"] = [model["id"] for model in data["data"]]
                    elif service == "anthropic" and "models" in data:
                        # Anthropic models data structure
                        info["models"] = data["models"]
                except Exception:
                    # If we can't parse models, that's okay
                    pass
            else:
                info["valid"] = False
        except Exception:
            # Request failed, key is probably invalid
            info["valid"] = False
    
    def update_key(self, service: str, key: str) -> bool:
        """
        Update an existing API key.
        
        Args:
            service: Service name (e.g., "openai", "anthropic")
            key: New API key for the service
            
        Returns:
            True if successful, False otherwise
        """
        if not key:
            return False
            
        # Check if service exists and where it's stored
        if service in self.services_info:
            source = self.services_info[service]["source"]
            if source == "environment":
                # Update in environment
                env_var = self.ENV_PREFIXES.get(service, f"{service.upper()}_API_KEY")
                os.environ[env_var] = key
                
                # Update our services info
                self.services_info[service]["api_key"] = key
                self.services_info[service]["valid"] = None  # Reset validation
                self.services_info[service]["models"] = []   # Reset models
                
                # Validate the updated key
                self._validate_service_key(service)
                return True
            elif source == "file":
                # Update in file
                return self.add_key(service, key, env=False)
        
        # If service doesn't exist, add it
        return self.add_key(service, key, env=False)
    
    def available_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available services and models.
        
        Returns:
            Dictionary mapping service names to info about keys and models
        """
        # Return a copy to avoid external modification
        return {service: info.copy() for service, info in self.services_info.items()}
    
    @staticmethod
    def _get_api_key_static(
        service: str,
        api_key: Optional[str] = None,
        keys_file: Optional[str] = None,
        use_env: bool = True,
    ) -> str:
        """
        Static method for getting API key for backwards compatibility.
        
        The priority order is:
        1. Direct api_key parameter
        2. Keys file (if specified)
        3. Local keys file (.keys.json in current directory)
        4. User keys file (~/.aipitboss_keys.json)
        5. Environment variable
        
        Args:
            service: Service name (e.g., "openai", "anthropic", "huggingface")
            api_key: Optional explicit API key
            keys_file: Optional path to a custom keys file
            use_env: Whether to check environment variables
            
        Returns:
            API key if found
            
        Raises:
            ValueError: If API key is not found in any source
        """
        # 1. Use direct API key if provided
        if api_key:
            return api_key
        
        # 2. Try to load from specified keys file
        if keys_file and os.path.exists(keys_file):
            key = KeyManager._load_from_file(keys_file, service)
            if key:
                return key
        
        # 3. Try to load from local keys file
        if os.path.exists(KeyManager.LOCAL_KEYS_FILE):
            key = KeyManager._load_from_file(KeyManager.LOCAL_KEYS_FILE, service)
            if key:
                return key
        
        # 4. Try to load from default keys file in user's home directory
        if os.path.exists(KeyManager.DEFAULT_KEYS_FILE):
            key = KeyManager._load_from_file(KeyManager.DEFAULT_KEYS_FILE, service)
            if key:
                return key
        
        # 5. Try to load from environment variable
        if use_env and service in KeyManager.ENV_PREFIXES:
            env_var = KeyManager.ENV_PREFIXES[service]
            key = os.environ.get(env_var)
            if key:
                return key
        
        # If no API key is found, raise an error
        raise ValueError(
            f"API key for {service} not found. Please provide it directly, "
            f"in a keys file, or set the {KeyManager.ENV_PREFIXES.get(service, service.upper() + '_API_KEY')} "
            "environment variable."
        )
    
    @staticmethod
    def _load_from_file(file_path: str, service: str) -> Optional[str]:
        """
        Load API key from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            service: Service name
            
        Returns:
            API key if found, None otherwise
        """
        try:
            with open(file_path, 'r') as f:
                keys = json.load(f)
                
            # Try to get the key using various possible formats
            if service in keys:
                return keys[service]
            
            service_key = f"{service}_api_key"
            if service_key in keys:
                return keys[service_key]
            
            service_caps = service.upper()
            if service_caps in keys:
                return keys[service_caps]
            
            service_caps_key = f"{service_caps}_API_KEY"
            if service_caps_key in keys:
                return keys[service_caps_key]
                
            return None
        
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    @staticmethod
    def save_keys(
        keys: Dict[str, str],
        file_path: Optional[str] = None,
    ) -> None:
        """
        Save API keys to a JSON file.
        
        Args:
            keys: Dictionary of service names to API keys
            file_path: Path to the JSON file (defaults to local .keys.json)
        """
        file_path = file_path or KeyManager.LOCAL_KEYS_FILE
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Load existing keys if the file exists
        existing_keys = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    existing_keys = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Update with new keys
        existing_keys.update(keys)
        
        # Write updated keys to file
        with open(file_path, 'w') as f:
            json.dump(existing_keys, f, indent=2) 