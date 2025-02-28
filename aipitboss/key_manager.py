"""
Key Management module for AIPitBoss package.

This module provides utilities for loading and managing API keys
from different sources (environment variables, key files, or direct input).
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any, Union


class KeyManager:
    """
    A class to manage API keys for different services.
    
    This class provides methods to load API keys from environment variables,
    from a key file, or directly from parameters.
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
    
    @staticmethod
    def get_api_key(
        service: str,
        api_key: Optional[str] = None,
        keys_file: Optional[str] = None,
        use_env: bool = True,
    ) -> str:
        """
        Get API key for a specific service from various sources.
        
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