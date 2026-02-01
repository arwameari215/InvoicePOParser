"""
ERPNext Configuration Module

Manages ERPNext connection settings and environment variables.
"""

import os
from typing import Optional


class ERPNextConfig:
    """ERPNext configuration management."""
    
    def __init__(self):
        """Initialize ERPNext configuration from environment variables."""
        self.url = os.getenv('ERPNEXT_URL', 'http://localhost:8080')
        self.api_key = os.getenv('ERPNEXT_API_KEY')
        self.api_secret = os.getenv('ERPNEXT_API_SECRET')
    
    def get_base_url(self) -> str:
        """
        Get the base URL for ERPNext instance.
        
        Returns:
            str: ERPNext base URL
        """
        return self.url
    
    def get_auth_header(self) -> str:
        """
        Get the authorization header value.
        
        Returns:
            str: Authorization header value in format "token {api_key}:{api_secret}"
        
        Raises:
            ValueError: If API credentials are not configured
        """
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "ERPNext API credentials not configured. "
                "Please set ERPNEXT_API_KEY and ERPNEXT_API_SECRET environment variables."
            )
        return f"token {self.api_key}:{self.api_secret}"
    
    def get_headers(self) -> dict:
        """
        Get complete headers for ERPNext API requests.
        
        Returns:
            dict: Headers dictionary with Authorization and Content-Type
        
        Raises:
            ValueError: If API credentials are not configured
        """
        return {
            'Authorization': self.get_auth_header(),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def is_configured(self) -> bool:
        """
        Check if ERPNext credentials are properly configured.
        
        Returns:
            bool: True if credentials are set, False otherwise
        """
        return bool(self.api_key and self.api_secret)


# Global configuration instance
erpnext_config = ERPNextConfig()
