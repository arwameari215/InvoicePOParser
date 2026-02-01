"""
API Integration Tests - Health Check Endpoints.

Tests /, /health, and /supported-types endpoints.
"""

import unittest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from tests.base.base_test_case import BaseTestCase
from tests.integration.api_clients.health_api_client import HealthAPIClient
from app.main import app
from app.parser_factory import ParserFactory


class TestHealthAPI(BaseTestCase):
    """
    Test suite for health check endpoints.
    
    Validates:
    - GET / returns correct welcome message
    - GET /health returns healthy status
    - GET /supported-types returns correct document types
    """
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        # Reset singleton state between tests
        ParserFactory._claude_service = None
        self.client = TestClient(app)
        self.health_client = HealthAPIClient(self.client)
    
    def tearDown(self):
        """Clean up test fixtures."""
        super().tearDown()
        # Reset singleton
        ParserFactory._claude_service = None
    
    def test_root_endpoint_returns_200(self):
        """
        Test that root endpoint returns 200 with API information.
        
        Validates:
        - HTTP 200 response
        - Contains message field
        - Contains version field
        - Contains endpoints field
        """
        # Act
        response = self.health_client.check_root()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('message', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        
        # Verify message indicates service is running
        self.assertIn('running', data['message'].lower())
    
    def test_health_endpoint_returns_200(self):
        """
        Test that /health endpoint returns 200 with healthy status.
        
        Validates:
        - HTTP 200 response
        - Contains status field
        - Status is "healthy"
        - Contains service field
        """
        # Act
        response = self.health_client.check_health()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        
        self.assertIn('service', data)
        self.assertEqual(data['service'], 'DocIntelligenceAPI')
    
    def test_supported_types_endpoint_returns_200(self):
        """
        Test that /supported-types returns correct document types.
        
        Validates:
        - HTTP 200 response
        - Contains supported_types field
        - supported_types is a list
        - Contains invoice and po types
        """
        # Act
        response = self.health_client.get_supported_types()
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('supported_types', data)
        self.assertIsInstance(data['supported_types'], list)
        
        # Verify expected document types
        supported = data['supported_types']
        self.assertIn('invoice', supported)
        self.assertIn('po', supported)
        self.assertIn('purchase_order', supported)
    
    def test_root_endpoint_structure(self):
        """
        Test that root endpoint has complete structure.
        
        Validates:
        - All expected keys present
        - Values are non-empty strings
        """
        # Act
        response = self.health_client.check_root()
        
        # Assert
        data = response.json()
        
        # Check required keys exist
        required_keys = ['message', 'version', 'endpoints']
        for key in required_keys:
            self.assertIn(key, data)
        
        # Validate string fields
        self.assertIsInstance(data['message'], str)
        self.assertGreater(len(data['message']), 0)
        self.assertIsInstance(data['version'], str)
        self.assertGreater(len(data['version']), 0)
        
        # Validate endpoints is a dict
        self.assertIsInstance(data['endpoints'], dict)
        self.assertGreater(len(data['endpoints']), 0)
    
    def test_health_using_helper_method(self):
        """
        Test health check using helper assertion method.
        
        Validates:
        - Helper method works correctly
        - Service is reported as healthy
        """
        # Act
        response = self.health_client.check_health()
        
        # Assert
        self.health_client.assert_healthy(response)
    
    def test_root_has_endpoints_info_using_helper(self):
        """
        Test root endpoint has endpoints info using helper.
        
        Validates:
        - Helper method works correctly
        - Endpoints information present
        """
        # Act
        response = self.health_client.check_root()
        
        # Assert
        self.health_client.assert_has_endpoints_info(response)
    
    def test_supported_types_no_duplicates(self):
        """
        Test that supported types list has no duplicates.
        
        Validates:
        - List contains unique values only
        """
        # Act
        response = self.health_client.get_supported_types()
        
        # Assert
        data = response.json()
        supported = data['supported_types']
        
        # Check for duplicates
        self.assertEqual(len(supported), len(set(supported)),
                        f"Duplicate types found: {supported}")
    
    def test_supported_types_are_lowercase(self):
        """
        Test that all supported types are lowercase.
        
        Validates:
        - Consistent lowercase naming
        """
        # Act
        response = self.health_client.get_supported_types()
        
        # Assert
        data = response.json()
        supported = data['supported_types']
        
        for doc_type in supported:
            self.assertEqual(doc_type, doc_type.lower(),
                           f"Type '{doc_type}' is not lowercase")


if __name__ == '__main__':
    unittest.main()
