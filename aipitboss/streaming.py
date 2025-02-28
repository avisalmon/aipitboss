"""
Streaming utilities for AIPitBoss package.

This module provides utilities for handling streaming responses
from AI APIs like OpenAI and Anthropic.
"""

import json
from typing import Iterator, Dict, Any, Callable, Optional


class StreamProcessor:
    """
    A utility class for processing streaming responses from AI APIs.
    
    This class provides methods for handling streaming responses and
    extracting content chunks as they arrive.
    """
    
    @staticmethod
    def process_openai_stream(
        response_iterator: Iterator[bytes],
        chunk_handler: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Process an OpenAI streaming response.
        
        Args:
            response_iterator: Iterator of bytes from a streaming response
            chunk_handler: Optional function to handle each content chunk
            
        Returns:
            Concatenated content from all chunks
        """
        full_content = ""
        
        for line in response_iterator:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Remove the "data: " prefix and parse JSON
            if line.startswith(b"data: "):
                data = line[6:]
                if data.strip() == b"[DONE]":
                    break
                    
                try:
                    chunk = json.loads(data)
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            content = delta["content"]
                            full_content += content
                            
                            # Call the chunk handler if provided
                            if chunk_handler:
                                chunk_handler(content)
                except Exception:
                    continue
        
        return full_content
    
    @staticmethod
    def process_anthropic_stream(
        response_iterator: Iterator[bytes],
        chunk_handler: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Process an Anthropic streaming response.
        
        Args:
            response_iterator: Iterator of bytes from a streaming response
            chunk_handler: Optional function to handle each content chunk
            
        Returns:
            Concatenated content from all chunks
        """
        full_content = ""
        
        for line in response_iterator:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Parse event data
            if line.startswith(b"data: "):
                data = line[6:]
                
                try:
                    chunk = json.loads(data)
                    
                    # Handle messages API format
                    if "type" in chunk and chunk["type"] == "content_block_delta":
                        if "delta" in chunk and "text" in chunk["delta"]:
                            content = chunk["delta"]["text"]
                            full_content += content
                            
                            # Call the chunk handler if provided
                            if chunk_handler:
                                chunk_handler(content)
                    
                    # Handle completions API format
                    elif "completion" in chunk:
                        content = chunk["completion"]
                        full_content += content
                        
                        # Call the chunk handler if provided
                        if chunk_handler:
                            chunk_handler(content)
                except Exception:
                    continue
        
        return full_content
    
    @staticmethod
    def print_stream(content: str) -> None:
        """
        Simple print handler for streaming content.
        
        Args:
            content: Content chunk to print
        """
        print(content, end="", flush=True) 