"""
AIPitBoss Package

A Python package for simplified interaction with AI services.
"""

__version__ = '0.1.0'

from .api_connect import APIConnect
from .ai_services import OpenAIService
from .utils import retry, format_prompt, parse_json_response, extract_text_from_response
from .streaming import StreamProcessor
from .key_manager import KeyManager
from .chat import Chat

__all__ = [
    'APIConnect',
    'OpenAIService',
    'Chat',
    'retry',
    'format_prompt',
    'parse_json_response',
    'extract_text_from_response',
    'StreamProcessor',
    'KeyManager',
]
