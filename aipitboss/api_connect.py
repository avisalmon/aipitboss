"""
API Connection module for AIPitBoss package.

This module provides a class for connecting to various APIs.
"""

import requests
from typing import Dict, Any, Optional, Union
import json


class APIConnect:
    """
    A class to handle API connections and requests.
    
    This class simplifies the process of connecting to APIs by handling
    authentication, base URLs, and common request operations.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """
        Initialize an API connection.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            headers: Additional headers to include in requests
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        # Set up default headers
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        # Update with any additional headers
        if headers:
            self.headers.update(headers)
            
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
    
    def _make_url(self, endpoint: str) -> str:
        """
        Construct the full URL for an API endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL for the API request
        """
        # Ensure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'
        return f'{self.base_url}{endpoint}'
    
    def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional parameters to pass to requests.get
            
        Returns:
            JSON response as a dictionary
        """
        url = self._make_url(endpoint)
        response = self.session.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def post(
        self, 
        endpoint: str, 
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: API endpoint
            data: Data to send in the body (string or dict)
            json_data: JSON data to send in the body
            **kwargs: Additional parameters to pass to requests.post
            
        Returns:
            JSON response as a dictionary
        """
        url = self._make_url(endpoint)
        
        # Convert data to JSON string if it's a dictionary
        if isinstance(data, dict):
            data = json.dumps(data)
            
        response = self.session.post(
            url,
            headers=self.headers,
            data=data,
            json=json_data,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def put(
        self, 
        endpoint: str, 
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a PUT request to the API.
        
        Args:
            endpoint: API endpoint
            data: Data to send in the body (string or dict)
            json_data: JSON data to send in the body
            **kwargs: Additional parameters to pass to requests.put
            
        Returns:
            JSON response as a dictionary
        """
        url = self._make_url(endpoint)
        
        # Convert data to JSON string if it's a dictionary
        if isinstance(data, dict):
            data = json.dumps(data)
            
        response = self.session.put(
            url,
            headers=self.headers,
            data=data,
            json=json_data,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def delete(
        self, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a DELETE request to the API.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional parameters to pass to requests.delete
            
        Returns:
            JSON response as a dictionary
        """
        url = self._make_url(endpoint)
        response = self.session.delete(
            url,
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
