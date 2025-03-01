import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from aipitboss.key_manager import KeyManager

# Test fixtures
@pytest.fixture
def sample_keys():
    return {
        "openai": "test-openai-key",
        "anthropic": "test-anthropic-key",
        "huggingface": "test-huggingface-key"
    }

@pytest.fixture
def temp_keys_file(sample_keys):
    # Create a temporary keys file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_keys, f)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Clean up the temporary file
    os.unlink(temp_file_path)

# Tests
def test_get_api_key_direct():
    """Test getting API key directly provided."""
    api_key = KeyManager.get_api_key(
        service="openai",
        api_key="direct-key",
        keys_file=None,
        use_env=False
    )
    
    assert api_key == "direct-key"

def test_get_api_key_from_file(temp_keys_file):
    """Test getting API key from keys file."""
    api_key = KeyManager.get_api_key(
        service="openai",
        api_key=None,
        keys_file=temp_keys_file,
        use_env=False
    )
    
    assert api_key == "test-openai-key"

def test_get_api_key_from_env(monkeypatch):
    """Test getting API key from environment variable."""
    # Set up environment variable
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    
    # Patch os.path.exists to make sure no keys file is found
    with patch('os.path.exists', return_value=False):
        api_key = KeyManager.get_api_key(
            service="openai",
            api_key=None,
            keys_file=None,
            use_env=True
        )
        
        assert api_key == "env-key"

def test_get_api_key_priority(temp_keys_file, monkeypatch):
    """Test the priority order of API key sources."""
    # Set up environment variable
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    
    # Direct key should take priority
    api_key = KeyManager.get_api_key(
        service="openai",
        api_key="direct-key",
        keys_file=temp_keys_file,
        use_env=True
    )
    assert api_key == "direct-key"
    
    # File should take priority over env
    api_key = KeyManager.get_api_key(
        service="openai",
        api_key=None,
        keys_file=temp_keys_file,
        use_env=True
    )
    assert api_key == "test-openai-key"

def test_get_api_key_not_found():
    """Test when no API key is found."""
    # The KeyManager now raises ValueError when no key is found
    with pytest.raises(ValueError, match="API key for nonexistent not found"):
        KeyManager.get_api_key(
            service="nonexistent",
            api_key=None,
            keys_file=None,
            use_env=False
        )

def test_save_keys():
    """Test saving keys to a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        keys_file = os.path.join(temp_dir, "test_keys.json")
        test_keys = {
            "service1": "key1",
            "service2": "key2"
        }
        
        # Save the keys
        KeyManager.save_keys(test_keys, keys_file)
        
        # Verify the file was created with the correct content
        assert os.path.exists(keys_file)
        
        with open(keys_file, 'r') as f:
            saved_keys = json.load(f)
        
        assert saved_keys == test_keys

def test_save_keys_with_existing_file(temp_keys_file, sample_keys):
    """Test merging with existing keys when saving."""
    # Add a new key
    new_keys = {"newservice": "new-key"}
    
    # Save and merge with existing file
    KeyManager.save_keys(new_keys, temp_keys_file)
    
    # Check the result
    with open(temp_keys_file, 'r') as f:
        saved_keys = json.load(f)
    
    # Should contain both the original and new keys
    expected = {**sample_keys, **new_keys}
    assert saved_keys == expected

def test_save_keys_overwrite(temp_keys_file):
    """Test overwriting existing keys."""
    # New value for an existing key
    update_keys = {"openai": "updated-key"}
    
    # Save and merge with existing file
    KeyManager.save_keys(update_keys, temp_keys_file)
    
    # Check the result
    with open(temp_keys_file, 'r') as f:
        saved_keys = json.load(f)
    
    # The openai key should be updated
    assert saved_keys["openai"] == "updated-key"
    # Other keys should still exist
    assert "anthropic" in saved_keys
    assert "huggingface" in saved_keys 