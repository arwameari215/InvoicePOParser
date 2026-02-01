"""
ERPNext API Endpoint Tests

Tests for all ERPNext integration API endpoints with mocked dependencies.
These tests validate:
- Endpoint routing and response structure
- Input validation
- Error handling
- Response formatting

These tests use MOCKS for ERPNext services (no real ERPNext connection required).
"""

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.main import app
from tests.integration.helpers.erpnext_fixtures import ERPNextFixtures


class TestERPNextAPIEndpoints(unittest.TestCase):
    """Test ERPNext integration API endpoints."""
    
    def setUp(self):
        """Set up test client and fixtures."""
        self.client = TestClient(app)
        self.fixtures = ERPNextFixtures()
    
    # ========================================================================
    # Connection Test Endpoint
    # ========================================================================
    
    @patch('app.routers.erpnext.test_connection')
    def test_erpnext_test_connection_success(self, mock_test_connection):
        """Test /erpnext/test-connection endpoint with successful connection."""
        # Mock successful connection
        mock_test_connection.return_value = {
            'success': True,
            'message': 'Successfully connected to ERPNext'
        }
        
        response = self.client.get("/erpnext/test-connection")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('Successfully connected', data['message'])
    
    @patch('app.routers.erpnext.test_connection')
    def test_erpnext_test_connection_failure(self, mock_test_connection):
        """Test /erpnext/test-connection endpoint with failed connection."""
        # Mock failed connection
        mock_test_connection.return_value = {
            'success': False,
            'error': 'Connection refused'
        }
        
        response = self.client.get("/erpnext/test-connection")
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    # ========================================================================
    # Company Endpoint
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_company_success(self, mock_get_entity):
        """Test GET /erpnext/company/{name} with existing company."""
        mock_company = {
            'name': 'Test Company',
            'company_name': 'Test Company',
            'abbr': 'TC',
            'default_currency': 'USD'
        }
        mock_get_entity.return_value = mock_company
        
        response = self.client.get("/erpnext/company/Test%20Company")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Test Company')
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_company_not_found(self, mock_get_entity):
        """Test GET /erpnext/company/{name} with non-existent company."""
        mock_get_entity.return_value = None
        
        response = self.client.get("/erpnext/company/NonExistent")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'].lower())
    
    # ========================================================================
    # Supplier Endpoint
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_supplier_success(self, mock_get_entity):
        """Test GET /erpnext/supplier/{name} with existing supplier."""
        mock_supplier = {
            'name': 'Test Supplier',
            'supplier_name': 'Test Supplier',
            'supplier_group': 'All Supplier Groups'
        }
        mock_get_entity.return_value = mock_supplier
        
        response = self.client.get("/erpnext/supplier/Test%20Supplier")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['supplier_name'], 'Test Supplier')
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_supplier_not_found(self, mock_get_entity):
        """Test GET /erpnext/supplier/{name} with non-existent supplier."""
        mock_get_entity.return_value = None
        
        response = self.client.get("/erpnext/supplier/NonExistent")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])
    
    # ========================================================================
    # Customer Endpoint
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_customer_success(self, mock_get_entity):
        """Test GET /erpnext/customer/{name} with existing customer."""
        mock_customer = {
            'name': 'Test Customer',
            'customer_name': 'Test Customer',
            'customer_group': 'All Customer Groups'
        }
        mock_get_entity.return_value = mock_customer
        
        response = self.client.get("/erpnext/customer/Test%20Customer")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['customer_name'], 'Test Customer')
    
    # ========================================================================
    # Item Endpoint
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_item_success(self, mock_get_entity):
        """Test GET /erpnext/item/{code} with existing item."""
        mock_item = {
            'name': 'ITEM-001',
            'item_code': 'ITEM-001',
            'item_name': 'Test Item',
            'stock_uom': 'Nos'
        }
        mock_get_entity.return_value = mock_item
        
        response = self.client.get("/erpnext/item/ITEM-001")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['item_code'], 'ITEM-001')
    
    # ========================================================================
    # Purchase Order Submission
    # ========================================================================
    
    @patch('app.routers.erpnext.submit_purchase_order_workflow')
    def test_submit_purchase_order_success(self, mock_workflow):
        """Test POST /erpnext/purchase-order with valid data."""
        # Mock successful workflow
        mock_workflow.return_value = {
            'po_name': 'PO-00001',
            'po_data': {
                'name': 'PO-00001',
                'supplier': 'Test Supplier',
                'docstatus': 1
            }
        }
        
        po_data = self.fixtures.get_test_purchase_order_data()
        
        response = self.client.post("/erpnext/purchase-order", json=po_data)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['po_name'], 'PO-00001')
        self.assertIn('status_log', data)
    
    @patch('app.routers.erpnext.submit_purchase_order_workflow')
    def test_submit_purchase_order_validation_error(self, mock_workflow):
        """Test POST /erpnext/purchase-order with invalid data."""
        from app.services.erpnext_service import ValidationError
        
        # Mock validation error
        mock_workflow.side_effect = ValidationError("Missing required field: company_name")
        
        po_data = self.fixtures.get_invalid_po_missing_company()
        
        response = self.client.post("/erpnext/purchase-order", json=po_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'validation')
        self.assertIn('Missing required field', data['error'])
    
    @patch('app.routers.erpnext.submit_purchase_order_workflow')
    def test_submit_purchase_order_connection_error(self, mock_workflow):
        """Test POST /erpnext/purchase-order with ERPNext connection error."""
        from app.services.erpnext_service import ConnectionError as ERPNextConnectionError
        
        # Mock connection error
        mock_workflow.side_effect = ERPNextConnectionError("Cannot connect to ERPNext")
        
        po_data = self.fixtures.get_test_purchase_order_data()
        
        response = self.client.post("/erpnext/purchase-order", json=po_data)
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'connection')
    
    # ========================================================================
    # Sales Invoice Submission
    # ========================================================================
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_submit_sales_invoice_success(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with valid data."""
        # Mock successful workflow
        mock_workflow.return_value = {
            'invoice_name': 'SINV-00001',
            'invoice_data': {
                'name': 'SINV-00001',
                'customer': 'Test Customer',
                'docstatus': 1
            }
        }
        
        invoice_data = self.fixtures.get_test_sales_invoice_data()
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['invoice_name'], 'SINV-00001')
        self.assertIn('status_log', data)
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_submit_sales_invoice_validation_error(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with invalid data."""
        from app.services.erpnext_service import ValidationError
        
        # Mock validation error
        mock_workflow.side_effect = ValidationError("Missing required field: customer_name")
        
        invoice_data = self.fixtures.get_invalid_invoice_missing_customer()
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'validation')
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_submit_sales_invoice_exchange_rate_error(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with exchange rate error."""
        from app.services.erpnext_service import ExchangeRateError
        
        # Mock exchange rate error
        mock_workflow.side_effect = ExchangeRateError("Exchange rate not found for EUR to USD")
        
        invoice_data = self.fixtures.get_test_sales_invoice_data()
        invoice_data['currency'] = 'EUR'
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'exchange_rate')


class TestERPNextAPIErrorHandling(unittest.TestCase):
    """Test error handling in ERPNext API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_company_api_error(self, mock_get_entity):
        """Test company endpoint handles ERPNext API errors gracefully."""
        from app.services.erpnext_service import ERPNextAPIError
        
        mock_get_entity.side_effect = ERPNextAPIError("ERPNext API error occurred")
        
        response = self.client.get("/erpnext/company/TestCompany")
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    @patch('app.routers.erpnext.submit_purchase_order_workflow')
    def test_po_submission_unexpected_error(self, mock_workflow):
        """Test PO endpoint handles unexpected errors gracefully."""
        # Mock unexpected exception
        mock_workflow.side_effect = Exception("Unexpected error occurred")
        
        po_data = ERPNextFixtures.get_test_purchase_order_data()
        
        response = self.client.post("/erpnext/purchase-order", json=po_data)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'unexpected')
        self.assertIn('Unexpected error', data['error'])


if __name__ == '__main__':
    unittest.main()
