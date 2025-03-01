import os
import json
import pytest
import tempfile
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock

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

# Tests for static methods (backward compatibility)
def test_get_api_key_direct():
    """Test getting API key directly provided."""
    api_key = KeyManager._get_api_key_static(
        service="openai",
        api_key="direct-key",
        keys_file=None,
        use_env=False
    )
    
    assert api_key == "direct-key"

def test_get_api_key_from_file(temp_keys_file):
    """Test getting API key from keys file."""
    api_key = KeyManager._get_api_key_static(
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
        api_key = KeyManager._get_api_key_static(
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
    api_key = KeyManager._get_api_key_static(
        service="openai",
        api_key="direct-key",
        keys_file=temp_keys_file,
        use_env=True
    )
    assert api_key == "direct-key"
    
    # File should take priority over env
    api_key = KeyManager._get_api_key_static(
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
        KeyManager._get_api_key_static(
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

# Tests for new instance methods
def test_keymanager_init(temp_keys_file, monkeypatch):
    """Test KeyManager initialization with keys from file."""
    # Patch the validate method to avoid actual API calls
    with patch.object(KeyManager, '_validate_keys'):
        km = KeyManager(keys_file=temp_keys_file, validate_keys=False)
        
        # Check that keys were loaded
        assert "openai" in km.services_info
        assert "anthropic" in km.services_info
        assert "huggingface" in km.services_info
        
        # Check service info structure
        assert km.services_info["openai"]["api_key"] == "test-openai-key"
        assert km.services_info["openai"]["source"] == "file"

def test_keymanager_init_from_env(monkeypatch):
    """Test KeyManager initialization with keys from environment."""
    # Set up environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "env-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-anthropic-key")
    
    # Patch the validate method to avoid actual API calls
    with patch.object(KeyManager, '_validate_keys'):
        # Use a non-existent keys file to force env vars
        km = KeyManager(keys_file="nonexistent.json", validate_keys=False)
        
        # Check that keys were loaded from environment
        assert "openai" in km.services_info
        assert "anthropic" in km.services_info
        
        # Check service info structure
        assert km.services_info["openai"]["api_key"] == "env-openai-key"
        assert km.services_info["openai"]["source"] == "environment"
        assert km.services_info["anthropic"]["api_key"] == "env-anthropic-key"
        assert km.services_info["anthropic"]["source"] == "environment"

def test_add_key_to_file():
    """Test adding a key to a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        keys_file = os.path.join(temp_dir, "test_keys.json")
        
        # Patch the validate method to avoid actual API calls
        with patch.object(KeyManager, '_validate_service_key'):
            km = KeyManager(keys_file=keys_file, validate_keys=False)
            
            # Add a key
            result = km.add_key("test-service", "test-key")
            
            # Check result
            assert result is True
            
            # Check that key was added to services_info
            assert "test-service" in km.services_info
            assert km.services_info["test-service"]["api_key"] == "test-key"
            assert km.services_info["test-service"]["source"] == "file"
            
            # Check that key was saved to file
            with open(keys_file, 'r') as f:
                saved_keys = json.load(f)
            
            assert saved_keys["test-service"] == "test-key"

def test_add_key_to_env():
    """Test adding a key to environment variables."""
    # Patch the validate method to avoid actual API calls
    with patch.object(KeyManager, '_validate_service_key'):
        km = KeyManager(validate_keys=False)
        
        # Add a key to environment
        result = km.add_key("test-service", "test-key", env=True)
        
        # Check result
        assert result is True
        
        # Check that key was added to services_info
        assert "test-service" in km.services_info
        assert km.services_info["test-service"]["api_key"] == "test-key"
        assert km.services_info["test-service"]["source"] == "environment"
        
        # Check that key was set in environment
        assert os.environ.get("TEST-SERVICE_API_KEY") == "test-key"

def test_update_key():
    """Test updating an existing key."""
    with tempfile.TemporaryDirectory() as temp_dir:
        keys_file = os.path.join(temp_dir, "test_keys.json")
        
        # Create initial key
        with open(keys_file, 'w') as f:
            json.dump({"test-service": "old-key"}, f)
        
        # Patch the validate method to avoid actual API calls
        with patch.object(KeyManager, '_validate_keys'):
            with patch.object(KeyManager, '_validate_service_key'):
                km = KeyManager(keys_file=keys_file, validate_keys=False)
                
                # Make sure the key was loaded
                assert "test-service" in km.services_info
                assert km.services_info["test-service"]["api_key"] == "old-key"
                
                # Update the key
                result = km.update_key("test-service", "new-key")
                
                # Check result
                assert result is True
                
                # Check that key was updated in services_info
                assert km.services_info["test-service"]["api_key"] == "new-key"
                
                # Check that key was updated in file
                with open(keys_file, 'r') as f:
                    saved_keys = json.load(f)
                
                assert saved_keys["test-service"] == "new-key"

def test_available_services():
    """Test getting available services information."""
    # Mock services info
    mock_services_info = {
        "service1": {
            "api_key": "key1",
            "source": "file",
            "valid": True,
            "models": ["model1", "model2"]
        },
        "service2": {
            "api_key": "key2",
            "source": "environment",
            "valid": False,
            "models": []
        }
    }
    
    # Patch the load and validate methods
    with patch.object(KeyManager, '_load_all_keys'):
        with patch.object(KeyManager, '_validate_keys'):
            km = KeyManager(validate_keys=False)
            km.services_info = mock_services_info
            
            # Get available services
            services = km.available_services()
            
            # Check result
            assert "service1" in services
            assert "service2" in services
            assert services["service1"]["valid"] is True
            assert services["service1"]["models"] == ["model1", "model2"]
            assert services["service2"]["valid"] is False
            
            # Check that it's a copy
            services["service1"]["api_key"] = "modified"
            assert km.services_info["service1"]["api_key"] == "key1"

@pytest.mark.live
def test_validate_keys_real():
    """Test validating real keys (requires valid API keys)."""
    # Skip if no keys file
    if not Path(".keys.json").exists():
        pytest.skip("No .keys.json file found for live API testing")
    
    # Create KeyManager with validation
    km = KeyManager(validate_keys=True)
    
    # Check services info
    services = km.available_services()
    
    # If OpenAI key is present, it should be validated
    if "openai" in services:
        assert "valid" in services["openai"]
        # Should have models if valid
        if services["openai"]["valid"]:
            assert len(services["openai"]["models"]) > 0 