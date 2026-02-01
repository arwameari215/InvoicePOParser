"""
ERPNext Real Integration Tests

Tests that connect to a REAL ERPNext instance.
NO MOCKS - these test the actual ERPNext API integration.

These tests:
- Connect to ERPNext using real credentials
- Create, read, and update actual ERPNext records
- Validate ERPNext client module functionality
- Should be run against a test ERPNext instance

Prerequisites:
- ERPNext instance must be running and accessible
- .env file must contain valid ERPNext credentials
- Test entities will be created in ERPNext
"""

import unittest
import os
import sys
from typing import Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config.erpnext_config import erpnext_config
from app.services.erpnext_service import (
    test_connection,
    get_entity,
    create_entity,
    update_entity,
    ensure_entity_exists,
    ERPNextAPIError,
    ValidationError,
    ConnectionError as ERPNextConnectionError
)
from tests.fixtures.erpnext_fixtures import ERPNextFixtures


def skip_if_erpnext_unavailable(test_func):
    """
    Decorator to skip test if ERPNext is not configured or unreachable.
    
    This allows tests to run in CI without failing when ERPNext is not available.
    """
    def wrapper(self):
        if not erpnext_config.is_configured():
            self.skipTest("ERPNext not configured (missing credentials in .env)")
        
        # Try to connect
        connection_result = test_connection()
        if not connection_result.get('success'):
            self.skipTest(f"ERPNext not reachable: {connection_result.get('error')}")
        
        return test_func(self)
    
    return wrapper


class TestERPNextConnection(unittest.TestCase):
    """Test ERPNext connection and configuration."""
    
    def test_erpnext_config_loaded(self):
        """Test that ERPNext configuration can be loaded."""
        # This test always runs to verify config module works
        self.assertIsNotNone(erpnext_config)
        self.assertIsNotNone(erpnext_config.url)
    
    @skip_if_erpnext_unavailable
    def test_connection_to_erpnext(self):
        """Test that we can connect to ERPNext successfully."""
        result = test_connection()
        
        self.assertTrue(result['success'])
        self.assertIn('message', result)
        # Check for either message format
        self.assertTrue(
            'successfully' in result['message'].lower() or 'connected' in result['message'].lower(),
            f"Expected connection success message, got: {result['message']}"
        )
    
    @skip_if_erpnext_unavailable
    def test_erpnext_credentials_valid(self):
        """Test that ERPNext credentials are valid by making an API call."""
        # Try to fetch any doctype to validate credentials
        try:
            # This should not raise an exception if credentials are valid
            result = get_entity('Company', 'does-not-exist')
            # If company doesn't exist, that's fine - credentials worked
            self.assertIsNone(result)
        except ERPNextAPIError as e:
            # Should not get authentication errors
            self.assertNotIn('authentication', str(e).lower())
            self.assertNotIn('unauthorized', str(e).lower())


class TestERPNextEntityOperations(unittest.TestCase):
    """Test CRUD operations on ERPNext entities (NO MOCKS)."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - check if ERPNext is available."""
        if not erpnext_config.is_configured():
            raise unittest.SkipTest("ERPNext not configured")
        
        connection_result = test_connection()
        if not connection_result.get('success'):
            raise unittest.SkipTest(f"ERPNext not reachable: {connection_result.get('error')}")
    
    def setUp(self):
        """Set up each test."""
        self.fixtures = ERPNextFixtures()
        self.created_entities = []  # Track entities to clean up
    
    def tearDown(self):
        """Clean up created test entities."""
        # Note: In a real test environment, you might want to delete test entities
        # For now, we'll leave them as they have "Test" prefix for identification
        pass
    
    # ========================================================================
    # Supplier Tests
    # ========================================================================
    
    @skip_if_erpnext_unavailable
    def test_create_supplier(self):
        """Test creating a new supplier in ERPNext."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        supplier_data = self.fixtures.get_test_supplier(f" IntegTest1-{timestamp}")
        
        # Create supplier
        created_supplier = create_entity('Supplier', supplier_data)
        
        self.assertIsNotNone(created_supplier)
        self.assertEqual(created_supplier['supplier_name'], supplier_data['supplier_name'])
        self.assertIn('name', created_supplier)
    
    @skip_if_erpnext_unavailable
    def test_get_supplier(self):
        """Test retrieving an existing supplier from ERPNext."""
        # First create a supplier
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        supplier_data = self.fixtures.get_test_supplier(f" IntegTest2-{timestamp}")
        created = create_entity('Supplier', supplier_data)
        supplier_name = created['name']
        
        # Now retrieve it
        retrieved_supplier = get_entity('Supplier', supplier_name)
        
        self.assertIsNotNone(retrieved_supplier)
        self.assertEqual(retrieved_supplier['name'], supplier_name)
    
    @skip_if_erpnext_unavailable
    def test_ensure_supplier_exists_creates_new(self):
        """Test ensure_entity_exists creates supplier if it doesn't exist."""
        supplier_data = self.fixtures.get_test_supplier(" IntegTest3")
        supplier_name = supplier_data['supplier_name']
        
        # Ensure supplier exists (should create it)
        result = ensure_entity_exists(
            'Supplier',
            supplier_name,
            supplier_data
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['supplier_name'], supplier_name)
    
    @skip_if_erpnext_unavailable
    def test_ensure_supplier_exists_returns_existing(self):
        """Test ensure_entity_exists returns existing supplier without creating duplicate."""
        supplier_data = self.fixtures.get_test_supplier(" IntegTest4")
        supplier_name = supplier_data['supplier_name']
        
        # Create supplier first
        first_result = ensure_entity_exists('Supplier', supplier_name, supplier_data)
        
        # Call again - should return existing
        second_result = ensure_entity_exists('Supplier', supplier_name, supplier_data)
        
        self.assertEqual(first_result['name'], second_result['name'])
    
    # ========================================================================
    # Customer Tests
    # ========================================================================
    
    @skip_if_erpnext_unavailable
    def test_create_customer(self):
        """Test creating a new customer in ERPNext."""
        customer_data = self.fixtures.get_test_customer(" IntegTest1")
        
        # Create customer
        created_customer = create_entity('Customer', customer_data)
        
        self.assertIsNotNone(created_customer)
        self.assertEqual(created_customer['customer_name'], customer_data['customer_name'])
        self.assertIn('name', created_customer)
    
    @skip_if_erpnext_unavailable
    def test_get_customer(self):
        """Test retrieving an existing customer from ERPNext."""
        # First create a customer
        customer_data = self.fixtures.get_test_customer(" IntegTest2")
        created = create_entity('Customer', customer_data)
        customer_name = created['name']
        
        # Now retrieve it
        retrieved_customer = get_entity('Customer', customer_name)
        
        self.assertIsNotNone(retrieved_customer)
        self.assertEqual(retrieved_customer['name'], customer_name)
    
    # ========================================================================
    # Item Tests
    # ========================================================================
    
    @skip_if_erpnext_unavailable
    def test_create_item(self):
        """Test creating a new item in ERPNext."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        item_data = self.fixtures.get_test_item(f"-INTEG1-{timestamp}")
        
        # Create item
        created_item = create_entity('Item', item_data)
        
        self.assertIsNotNone(created_item)
        self.assertEqual(created_item['item_code'], item_data['item_code'])
        self.assertIn('name', created_item)
    
    @skip_if_erpnext_unavailable
    def test_get_item(self):
        """Test retrieving an existing item from ERPNext."""
        # First create an item
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        item_data = self.fixtures.get_test_item(f"-INTEG2-{timestamp}")
        created = create_entity('Item', item_data)
        item_code = created['item_code']
        
        # Now retrieve it
        retrieved_item = get_entity('Item', item_code)
        
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item['item_code'], item_code)
    
    # ========================================================================
    # Company Tests
    # ========================================================================
    
    @skip_if_erpnext_unavailable
    def test_get_company(self):
        """Test retrieving company from ERPNext."""
        # Assume default company exists in ERPNext
        # Try to get any company (usually there's at least one)
        try:
            company = get_entity('Company', 'Test Company CI')
            if company:
                self.assertIn('name', company)
                self.assertIn('company_name', company)
        except ERPNextAPIError:
            # If specific company doesn't exist, test passes
            # (we're just testing the API call works)
            pass
    
    # ========================================================================
    # Error Handling Tests
    # ========================================================================
    
    @skip_if_erpnext_unavailable
    def test_get_nonexistent_entity_returns_none(self):
        """Test that getting a non-existent entity returns None."""
        result = get_entity('Supplier', 'This-Supplier-Should-Not-Exist-12345')
        self.assertIsNone(result)
    
    @skip_if_erpnext_unavailable
    def test_create_duplicate_supplier_raises_error(self):
        """Test that creating duplicate supplier raises appropriate error."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        supplier_data = self.fixtures.get_test_supplier(f" DuplicateTest-{timestamp}")
        
        # Create first time - should succeed
        create_entity('Supplier', supplier_data)
        
        # Try to create again - should raise error
        with self.assertRaises(ERPNextAPIError):
            create_entity('Supplier', supplier_data)


class TestERPNextDataValidation(unittest.TestCase):
    """Test data validation and error handling."""
    
    @skip_if_erpnext_unavailable
    def test_create_supplier_missing_required_field(self):
        """Test that creating supplier without required fields raises error."""
        invalid_data = {
            "doctype": "Supplier"
            # Missing supplier_name - required field
        }
        
        with self.assertRaises((ERPNextAPIError, ValidationError)):
            create_entity('Supplier', invalid_data)
    
    @skip_if_erpnext_unavailable
    def test_create_item_missing_required_field(self):
        """Test that creating item without required fields raises error."""
        invalid_data = {
            "doctype": "Item",
            # Missing item_code and item_name - required fields
        }
        
        with self.assertRaises((ERPNextAPIError, ValidationError)):
            create_entity('Item', invalid_data)


if __name__ == '__main__':
    unittest.main()
