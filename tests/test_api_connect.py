"""
Tests for the APIConnect class.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from aipitboss.api_connect import APIConnect


@pytest.fixture
def api_connect():
    """
    Fixture to create an APIConnect instance for testing.
    """
    return APIConnect(
        api_key="test_key",
        base_url="https://api.example.com/v1"
    )


def test_init():
    """
    Test that APIConnect is initialized correctly.
    """
    api = APIConnect(
        api_key="test_key",
        base_url="https://api.example.com/v1"
    )
    
    assert api.api_key == "test_key"
    assert api.base_url == "https://api.example.com/v1"
    assert api.headers["Authorization"] == "Bearer test_key"
    assert api.headers["Content-Type"] == "application/json"
    assert api.timeout == 30
    assert api.verify_ssl is True


def test_custom_headers():
    """
    Test that custom headers are properly set.
    """
    custom_headers = {
        "Content-Type": "application/json",
        "User-Agent": "AIPitBoss Test",
        "X-Custom-Header": "Custom Value"
    }
    
    api = APIConnect(
        api_key="test_key",
        base_url="https://api.example.com",
        headers=custom_headers
    )
    
    # Check that all custom headers are set
    assert api.headers["Content-Type"] == "application/json"
    assert api.headers["User-Agent"] == "AIPitBoss Test"
    assert api.headers["X-Custom-Header"] == "Custom Value"
    
    # Check that the Authorization header is also set
    assert "Authorization" in api.headers
    assert api.headers["Authorization"] == "Bearer test_key"


def test_make_url(api_connect):
    """
    Test URL construction.
    """
    # With leading slash
    url = api_connect._make_url("/endpoint")
    assert url == "https://api.example.com/v1/endpoint"
    
    # Without leading slash
    url = api_connect._make_url("endpoint")
    assert url == "https://api.example.com/v1/endpoint"


@patch("requests.Session.get")
def test_get(mock_get, api_connect):
    """
    Test GET request.
    """
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Make the request
    result = api_connect.get("/endpoint", params={"param": "value"})
    
    # Verify the result
    assert result == {"data": "test_data"}
    
    # Verify the mock was called correctly
    mock_get.assert_called_once_with(
        "https://api.example.com/v1/endpoint",
        headers=api_connect.headers,
        params={"param": "value"},
        timeout=30,
        verify=True
    )


@patch("requests.Session.post")
def test_post(mock_post, api_connect):
    """
    Test POST request.
    """
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Make the request with dictionary data
    result = api_connect.post("/endpoint", data={"key": "value"})
    
    # Verify the result
    assert result == {"data": "test_data"}
    
    # Verify the mock was called correctly - data should be converted to JSON string
    mock_post.assert_called_once_with(
        "https://api.example.com/v1/endpoint",
        headers=api_connect.headers,
        data='{"key": "value"}',
        json=None,
        timeout=30,
        verify=True
    )


@patch("requests.Session.put")
def test_put(mock_put, api_connect):
    """
    Test PUT request.
    """
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.raise_for_status.return_value = None
    mock_put.return_value = mock_response
    
    # Make the request with JSON data
    result = api_connect.put("/endpoint", json_data={"key": "value"})
    
    # Verify the result
    assert result == {"data": "test_data"}
    
    # Verify the mock was called correctly
    mock_put.assert_called_once_with(
        "https://api.example.com/v1/endpoint",
        headers=api_connect.headers,
        data=None,
        json={"key": "value"},
        timeout=30,
        verify=True
    )


@patch("requests.Session.put")
def test_put_with_dict_data(mock_put, api_connect):
    """
    Test PUT request with dictionary data.
    """
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test_data"}
    mock_response.raise_for_status.return_value = None
    mock_put.return_value = mock_response
    
    # Make the request with dictionary data
    result = api_connect.put("/endpoint", data={"key": "value"})
    
    # Verify the result
    assert result == {"data": "test_data"}
    
    # Verify the mock was called correctly - data should be converted to JSON string
    mock_put.assert_called_once_with(
        "https://api.example.com/v1/endpoint",
        headers=api_connect.headers,
        data='{"key": "value"}',
        json=None,
        timeout=30,
        verify=True
    )


@patch("requests.Session.delete")
def test_delete(mock_delete, api_connect):
    """
    Test DELETE request.
    """
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "deleted"}
    mock_response.raise_for_status.return_value = None
    mock_delete.return_value = mock_response
    
    # Make the request
    result = api_connect.delete("/endpoint")
    
    # Verify the result
    assert result == {"status": "deleted"}
    
    # Verify the mock was called correctly
    mock_delete.assert_called_once_with(
        "https://api.example.com/v1/endpoint",
        headers=api_connect.headers,
        timeout=30,
        verify=True
    ) 