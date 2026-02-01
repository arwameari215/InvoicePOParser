"""
Health API Client - Page Object for health check endpoints.

Encapsulates health check API operations.
"""

from .base_api_client import BaseAPIClient
from typing import Dict, Any


class HealthAPIClient(BaseAPIClient):
    """
    API client for health check endpoints.
    
    Provides methods for testing health-related endpoints.
    """
    
    def check_health(self):
        """
        Check the /health endpoint.
        
        Returns:
            Response object.
        """
        return self.get("/health")
    
    def check_root(self):
        """
        Check the root / endpoint.
        
        Returns:
            Response object.
        """
        return self.get("/")
    
    def get_supported_types(self):
        """
        Get supported document types from /supported-types.
        
        Returns:
            Response object.
        """
        return self.get("/supported-types")
    
    def assert_healthy(self, response):
        """
        Assert that health check response indicates healthy status.
        
        Args:
            response: Response from health endpoint.
        
        Raises:
            AssertionError: If service is not healthy.
        """
        self.assert_success_response(response, 200)
        data = response.json()
        
        if "status" in data:
            assert data["status"] == "healthy", f"Service not healthy: {data}"
        elif "message" in data:
            assert "running" in data["message"].lower(), f"Service not running: {data}"
    
    def assert_has_endpoints_info(self, response):
        """
        Assert that root endpoint returns endpoints information.
        
        Args:
            response: Response from root endpoint.
        
        Raises:
            AssertionError: If endpoints info is missing.
        """
        self.assert_success_response(response, 200)
        data = response.json()
        assert "endpoints" in data, "Missing endpoints information"
