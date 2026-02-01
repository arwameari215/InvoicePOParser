"""
Base API Client - Abstract base for all API Page Objects.

Provides common HTTP methods and response handling.
"""

from fastapi.testclient import TestClient
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Base API client for Page Object Model pattern in API testing.
    
    This class abstracts HTTP operations and provides a clean interface
    for making API requests in tests.
    """
    
    def __init__(self, client: TestClient):
        """
        Initialize base API client.
        
        Args:
            client: FastAPI TestClient instance.
        """
        self.client = client
        self.base_url = ""
    
    def get(self, path: str, **kwargs) -> Any:
        """
        Make a GET request.
        
        Args:
            path: API endpoint path.
            **kwargs: Additional request parameters.
        
        Returns:
            Response object.
        """
        logger.debug(f"GET {path}")
        response = self.client.get(path, **kwargs)
        logger.debug(f"Response: {response.status_code}")
        return response
    
    def post(self, path: str, **kwargs) -> Any:
        """
        Make a POST request.
        
        Args:
            path: API endpoint path.
            **kwargs: Additional request parameters.
        
        Returns:
            Response object.
        """
        logger.debug(f"POST {path}")
        response = self.client.post(path, **kwargs)
        logger.debug(f"Response: {response.status_code}")
        return response
    
    def put(self, path: str, **kwargs) -> Any:
        """
        Make a PUT request.
        
        Args:
            path: API endpoint path.
            **kwargs: Additional request parameters.
        
        Returns:
            Response object.
        """
        logger.debug(f"PUT {path}")
        response = self.client.put(path, **kwargs)
        logger.debug(f"Response: {response.status_code}")
        return response
    
    def delete(self, path: str, **kwargs) -> Any:
        """
        Make a DELETE request.
        
        Args:
            path: API endpoint path.
            **kwargs: Additional request parameters.
        
        Returns:
            Response object.
        """
        logger.debug(f"DELETE {path}")
        response = self.client.delete(path, **kwargs)
        logger.debug(f"Response: {response.status_code}")
        return response
    
    def assert_success_response(self, response, expected_status: int = 200):
        """
        Assert that response is successful.
        
        Args:
            response: Response object.
            expected_status: Expected HTTP status code.
        
        Raises:
            AssertionError: If response is not successful.
        """
        if response.status_code != expected_status:
            raise AssertionError(
                f"Expected status {expected_status}, got {response.status_code}. "
                f"Response: {response.text}"
            )
    
    def assert_error_response(self, response, expected_status: int = 400):
        """
        Assert that response is an error.
        
        Args:
            response: Response object.
            expected_status: Expected HTTP status code.
        
        Raises:
            AssertionError: If response is not an error.
        """
        if response.status_code != expected_status:
            raise AssertionError(
                f"Expected error status {expected_status}, got {response.status_code}"
            )
