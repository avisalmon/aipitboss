# Utility functions for AIPitBoss 

"""
Utility module for AIPitBoss package.

This module provides common utility functions for working with AI APIs,
including retry logic, prompt formatting, and response parsing.
"""

import json
import time
from typing import Dict, Any, Callable, Optional, Union, List, TypeVar

T = TypeVar('T')


def retry(
    func: Callable[..., T],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    errors_to_retry: tuple = (Exception,)
) -> T:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: The function to retry
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries in seconds
        backoff_factor: Factor to increase delay by after each retry
        errors_to_retry: Tuple of exceptions that should trigger a retry
        
    Returns:
        The result of the function
        
    Raises:
        Exception: The last exception raised by the function
    """
    last_exception = None
    delay = retry_delay
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except errors_to_retry as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise last_exception


def format_prompt(
    template: str,
    **kwargs
) -> str:
    """
    Format a prompt template with variables.
    
    Args:
        template: Prompt template with {variable} placeholders
        **kwargs: Variables to insert into the template
        
    Returns:
        Formatted prompt string
    """
    return template.format(**kwargs)


def parse_json_response(
    response: str, 
    default: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse a JSON response string, handling errors.
    
    Args:
        response: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON as a dictionary
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        if default is None:
            default = {}
        return default


def extract_text_from_response(
    response: Dict[str, Any],
    path: Union[str, List[str]],
    default: str = ""
) -> str:
    """
    Extract text from a nested response dictionary.
    
    Args:
        response: Response dictionary
        path: Path to the text value, either dot-separated string or list of keys
        default: Default value if path not found
        
    Returns:
        Extracted text
    """
    if isinstance(path, str):
        path = path.split(".")
        
    current = response
    try:
        for key in path:
            # Handle array indices in path (e.g., 'choices.0.text')
            if key.isdigit():
                key = int(key)
            current = current[key]
        return str(current)
    except (KeyError, IndexError, TypeError):
        return default 
