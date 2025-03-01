"""
API Connection module for AIPitBoss package.

This is a simple module for connecting to REST APIs.
"""

import json
import requests
from typing import Dict, Any, Optional, Union


class APIConnect:
    """
    A minimalist class for connecting to REST APIs.
    
    This class provides basic functionality for making HTTP requests
    to REST APIs with authentication.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        Initialize an API connection.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            headers: Optional additional headers to send with requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Set up default headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Add any custom headers
        if headers:
            self.headers.update(headers)
        
        # Create a session for connection pooling
        self.session = requests.Session()
    
    def _make_url(self, endpoint: str) -> str:
        """
        Construct a full URL from a base URL and endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Complete URL
        """
        # Make sure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
            
        return self.base_url + endpoint
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            API response as a dictionary
        """
        url = self._make_url(endpoint)
        response = self.session.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()
    
    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: API endpoint path
            data: Optional data to send (dict will be converted to JSON)
            json_data: Optional JSON data to send
            
        Returns:
            API response as a dictionary
        """
        url = self._make_url(endpoint)
        
        # If data is a dict, convert it to JSON
        if isinstance(data, dict):
            data = json.dumps(data)
            
        response = self.session.post(
            url,
            headers=self.headers,
            data=data,
            json=json_data,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()
    
    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a PUT request to the API.
        
        Args:
            endpoint: API endpoint path
            data: Optional data to send (dict will be converted to JSON)
            json_data: Optional JSON data to send
            
        Returns:
            API response as a dictionary
        """
        url = self._make_url(endpoint)
        
        # If data is a dict, convert it to JSON
        if isinstance(data, dict):
            data = json.dumps(data)
            
        response = self.session.put(
            url,
            headers=self.headers,
            data=data,
            json=json_data,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json()
    
    def delete(
        self,
        endpoint: str
    ) -> Dict[str, Any]:
        """
        Make a DELETE request to the API.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            API response as a dictionary
        """
        url = self._make_url(endpoint)
        response = self.session.delete(
            url,
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response.json() 