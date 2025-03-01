"""
Tests for the Chat class.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from aipitboss.chat import Chat
from aipitboss.ai_services import OpenAIService


@pytest.fixture
def openai_service_mock():
    """Mock OpenAI service for testing"""
    mock_service = MagicMock(spec=OpenAIService)
    mock_service.chat_completion.return_value = {
        "choices": [{"message": {"content": "Mock response"}}]
    }
    return mock_service


@pytest.fixture
def generic_service_mock():
    """Mock generic service for testing"""
    mock_service = MagicMock()
    mock_service.chat_completion.return_value = {
        "content": [{"text": "Mock response"}]
    }
    return mock_service


def test_chat_init(openai_service_mock):
    """Test Chat initialization"""
    chat = Chat(openai_service_mock)
    
    assert chat.service == openai_service_mock
    assert chat.system_message == "You are a helpful, concise assistant."
    assert len(chat.conversation_history) == 1
    assert chat.conversation_history[0]["role"] == "system"


def test_ask_question_openai(openai_service_mock):
    """Test ask_question with OpenAI service"""
    chat = Chat(openai_service_mock)
    response = chat.ask_question("Hello, world!")
    
    assert response == "Mock response"
    assert len(chat.conversation_history) == 3  # system + user + assistant
    assert chat.conversation_history[1]["role"] == "user"
    assert chat.conversation_history[1]["content"] == "Hello, world!"
    assert chat.conversation_history[2]["role"] == "assistant"
    assert chat.conversation_history[2]["content"] == "Mock response"


def test_ask_question_generic_service(generic_service_mock):
    """Test ask_question with a generic service"""
    chat = Chat(generic_service_mock)
    response = chat.ask_question("Hello, world!")
    
    assert response == "Mock response"
    assert len(chat.conversation_history) == 3  # system + user + assistant


def test_ask_alias(openai_service_mock):
    """Test that ask is an alias for ask_question"""
    chat = Chat(openai_service_mock)
    
    # Test that ask calls ask_question with the same arguments
    with patch.object(chat, 'ask_question') as mock_ask_question:
        mock_ask_question.return_value = "Response"
        response = chat.ask("Hello", temperature=0.8)
        
        mock_ask_question.assert_called_once_with("Hello", temperature=0.8)
        assert response == "Response"


def test_set_service(openai_service_mock, generic_service_mock):
    """Test changing the service"""
    chat = Chat(openai_service_mock)
    assert chat.service == openai_service_mock
    
    chat.setService(generic_service_mock)
    assert chat.service == generic_service_mock


def test_clear_history(openai_service_mock):
    """Test clearing conversation history"""
    chat = Chat(openai_service_mock)
    chat.ask_question("Hello")  # This adds to history
    
    assert len(chat.conversation_history) > 1
    
    chat.clear_history()
    assert len(chat.conversation_history) == 0


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
    
    # Create chat and ask a simple question
    chat = Chat(openai)
    response = chat.ask_question(
        "What is 2+2? Please answer with just the number.",
        max_tokens=10
    )
    
    # Check we got a meaningful response
    assert response
    assert "4" in response 