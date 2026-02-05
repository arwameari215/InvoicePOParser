"""
ERPNext API Error Handling Tests

Comprehensive tests for error paths in ERPNext router endpoints:
- API error handling for all GET endpoints
- All error types for POST endpoints (ValidationError, ExchangeRateError, ConnectionError, ERPNextAPIError, generic Exception)
- Customer and Item endpoint error paths
- 404 not found cases
"""

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.main import app
from app.services.erpnext_service import (
    ValidationError,
    ERPNextAPIError,
    ExchangeRateError,
    ConnectionError as ERPNextConnectionError
)
from tests.integration.helpers.erpnext_fixtures import ERPNextFixtures


class TestERPNextGetEndpointErrors(unittest.TestCase):
    """Test error handling for all ERPNext GET endpoints."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    # ========================================================================
    # Company Endpoint Error Tests
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_company_api_error_returns_500(self, mock_get_entity):
        """Test GET /erpnext/company/{name} handles ERPNext API error."""
        mock_get_entity.side_effect = ERPNextAPIError("ERPNext API error")
        
        response = self.client.get("/erpnext/company/TestCompany")
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertIn('ERPNext API error', data['error'])
    
    # ========================================================================
    # Supplier Endpoint Error Tests  
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_supplier_api_error_returns_500(self, mock_get_entity):
        """Test GET /erpnext/supplier/{name} handles ERPNext API error."""
        mock_get_entity.side_effect = ERPNextAPIError("ERPNext API error")
        
        response = self.client.get("/erpnext/supplier/TestSupplier")
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    # ========================================================================
    # Customer Endpoint Error Tests
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_customer_not_found_returns_404(self, mock_get_entity):
        """Test GET /erpnext/customer/{name} returns 404 when not found."""
        mock_get_entity.return_value = None
        
        response = self.client.get("/erpnext/customer/NonExistent")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'].lower())
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_customer_api_error_returns_500(self, mock_get_entity):
        """Test GET /erpnext/customer/{name} handles ERPNext API error."""
        mock_get_entity.side_effect = ERPNextAPIError("ERPNext API error")
        
        response = self.client.get("/erpnext/customer/TestCustomer")
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    # ========================================================================
    # Item Endpoint Error Tests
    # ========================================================================
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_item_not_found_returns_404(self, mock_get_entity):
        """Test GET /erpnext/item/{code} returns 404 when not found."""
        mock_get_entity.return_value = None
        
        response = self.client.get("/erpnext/item/NONEXISTENT-001")
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'].lower())
    
    @patch('app.routers.erpnext.get_entity')
    def test_get_item_api_error_returns_500(self, mock_get_entity):
        """Test GET /erpnext/item/{code} handles ERPNext API error."""
        mock_get_entity.side_effect = ERPNextAPIError("ERPNext API error")
        
        response = self.client.get("/erpnext/item/ITEM-001")
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)


class TestPurchaseOrderSubmissionErrors(unittest.TestCase):
    """Test all error paths for Purchase Order submission."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    @patch('app.routers.erpnext.submit_purchase_order_workflow')
    def test_po_exchange_rate_error_returns_400(self, mock_workflow):
        """Test POST /erpnext/purchase-order with ExchangeRateError."""
        mock_workflow.side_effect = ExchangeRateError("Exchange rate not found for EUR")
        
        po_data = ERPNextFixtures.get_test_purchase_order_data()
        
        response = self.client.post("/erpnext/purchase-order", json=po_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'exchange_rate')
        self.assertIn('Exchange rate', data['error'])
    
    @patch('app.routers.erpnext.submit_purchase_order_workflow')
    def test_po_api_error_returns_500(self, mock_workflow):
        """Test POST /erpnext/purchase-order with ERPNextAPIError."""
        mock_workflow.side_effect = ERPNextAPIError("ERPNext API error occurred")
        
        po_data = ERPNextFixtures.get_test_purchase_order_data()
        
        response = self.client.post("/erpnext/purchase-order", json=po_data)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'erpnext_api')
    
    @patch('app.routers.erpnext.submit_purchase_order_workflow')
    def test_po_unexpected_error_returns_500(self, mock_workflow):
        """Test POST /erpnext/purchase-order with unexpected Exception."""
        mock_workflow.side_effect = RuntimeError("Unexpected runtime error")
        
        po_data = ERPNextFixtures.get_test_purchase_order_data()
        
        response = self.client.post("/erpnext/purchase-order", json=po_data)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'unexpected')
        self.assertIn('Unexpected error', data['error'])


class TestSalesInvoiceSubmissionErrors(unittest.TestCase):
    """Test all error paths for Sales Invoice submission."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_invoice_validation_error_returns_400(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with ValidationError."""
        mock_workflow.side_effect = ValidationError("Missing customer_name")
        
        invoice_data = ERPNextFixtures.get_test_sales_invoice_data()
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'validation')
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_invoice_exchange_rate_error_returns_400(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with ExchangeRateError."""
        mock_workflow.side_effect = ExchangeRateError("Exchange rate not found")
        
        invoice_data = ERPNextFixtures.get_test_sales_invoice_data()
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'exchange_rate')
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_invoice_connection_error_returns_503(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with ConnectionError."""
        mock_workflow.side_effect = ERPNextConnectionError("Cannot connect to ERPNext")
        
        invoice_data = ERPNextFixtures.get_test_sales_invoice_data()
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'connection')
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_invoice_api_error_returns_500(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with ERPNextAPIError."""
        mock_workflow.side_effect = ERPNextAPIError("ERPNext API error")
        
        invoice_data = ERPNextFixtures.get_test_sales_invoice_data()
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'erpnext_api')
    
    @patch('app.routers.erpnext.submit_sales_invoice_workflow')
    def test_invoice_unexpected_error_returns_500(self, mock_workflow):
        """Test POST /erpnext/sales-invoice with unexpected Exception."""
        mock_workflow.side_effect = KeyError("Unexpected key error")
        
        invoice_data = ERPNextFixtures.get_test_sales_invoice_data()
        
        response = self.client.post("/erpnext/sales-invoice", json=invoice_data)
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error_type'], 'unexpected')


if __name__ == '__main__':
    unittest.main()
