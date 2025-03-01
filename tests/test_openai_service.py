"""
Tests for the OpenAIService class.
"""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from aipitboss.ai_services import OpenAIService
from aipitboss.key_manager import KeyManager


@pytest.fixture
def mock_api_response():
    """Mock API response for OpenAI requests"""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock response.",
                    "role": "assistant"
                }
            }
        ]
    }


def test_openai_service_init_with_api_key():
    """Test OpenAIService initialization with direct API key"""
    service = OpenAIService(api_key="test-key")
    
    assert hasattr(service, 'api')
    assert service.api.api_key == "test-key"


def test_openai_service_init_with_service_name():
    """Test OpenAIService initialization with service name and mocked keys file"""
    with patch.object(KeyManager, 'get_api_key', return_value="test-key"):
        service = OpenAIService("openai")
    
    assert hasattr(service, 'api')
    assert service.api.api_key == "test-key"


def test_get_services():
    """Test get_services method for listing available services"""
    # Create temporary keys file
    temp_file = "temp_keys.json"
    with open(temp_file, 'w') as f:
        json.dump({"openai": "test-key", "anthropic": "test-key2"}, f)
    
    try:
        service = OpenAIService(keys_file=temp_file)
        services = service.get_services()
        
        assert isinstance(services, list)
        assert "openai" in services
        assert "anthropic" in services
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_set_service():
    """Test set_service method for changing the service provider"""
    # Create temporary keys file with test services
    temp_keys = {
        "service1": "key1",
        "service2": "key2"
    }
    
    with patch('builtins.open', create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = json.dumps(temp_keys)
        
        # Initialize with first service
        with patch.object(KeyManager, 'get_api_key', return_value="key1"):
            service = OpenAIService("service1")
            
            # Test initial state
            assert service.service_name == "service1"
            assert service.api.api_key == "key1"
            
            # Test changing to valid service
            with patch.object(KeyManager, 'get_api_key', return_value="key2"):
                service.set_service("service2")
                assert service.service_name == "service2"
                assert service.api.api_key == "key2"
            
            # Test invalid service
            with patch.object(KeyManager, 'get_api_key', side_effect=ValueError):
                # Should return False instead of raising an exception
                result = service.set_service("nonexistent")
                assert result is False


@patch('aipitboss.api_connect.APIConnect.post')
def test_chat_completion(mock_post, mock_api_response):
    """Test chat_completion method"""
    mock_post.return_value = mock_api_response
    
    service = OpenAIService(api_key="test-key")
    messages = [{"role": "user", "content": "Hello"}]
    
    response = service.chat_completion(messages, model="gpt-3.5-turbo")
    
    mock_post.assert_called_once()
    assert response == mock_api_response


@pytest.mark.live
def test_real_openai_connection():
    """Test a real connection to OpenAI API (requires valid API key)"""
    # Skip if no API key
    keys_file = Path(".keys.json")
    if not keys_file.exists():
        pytest.skip("No .keys.json file found for live API testing")
    
    # Initialize service with key from file
    openai = OpenAIService("openai", keys_file=str(keys_file))
    
    # Skip if service initialization failed
    if not hasattr(openai, 'api') or not hasattr(openai.api, 'api_key'):
        pytest.skip("Failed to initialize OpenAI service with valid API key")
    
    # Make a simple request
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2? Respond with just the number."}
    ]
    
    response = openai.chat_completion(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=10
    )
    
    # Check we got a valid response
    assert "choices" in response
    assert len(response["choices"]) > 0
    assert "message" in response["choices"][0]
    assert "content" in response["choices"][0]["message"]
    assert "4" in response["choices"][0]["message"]["content"] 