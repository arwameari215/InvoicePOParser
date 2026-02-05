"""
ERPNext Workflow Integration Tests

Tests complete end-to-end workflows that interact with real ERPNext.
NO MOCKS - these test actual Purchase Order and Sales Invoice creation.

These tests validate:
- Complete workflow from parsed data to ERPNext submission
- Entity auto-creation (suppliers, customers, items)
- Data transformation and validation
- Error handling in workflows
"""

import unittest
import os
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.config.erpnext_config import erpnext_config
from app.services.erpnext_service import check_erpnext_connection
from app.workflows.erpnext_workflows import (
    submit_purchase_order_workflow,
    submit_sales_invoice_workflow
)
from tests.integration.helpers.erpnext_fixtures import ERPNextFixtures


def skip_if_erpnext_unavailable(test_func):
    """Decorator to skip test if ERPNext is not available."""
    def wrapper(self):
        if not erpnext_config.is_configured():
            self.skipTest("ERPNext not configured")
        
        connection_result = check_erpnext_connection()
        if not connection_result.get('success'):
            self.skipTest(f"ERPNext not reachable: {connection_result.get('error')}")
        
        return test_func(self)
    
    return wrapper


class TestPurchaseOrderWorkflow(unittest.TestCase):
    """Test complete Purchase Order workflow with real ERPNext."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fixtures = ERPNextFixtures()
        self.status_messages = []
    
    def status_callback(self, message: str):
        """Callback to capture workflow status messages."""
        self.status_messages.append(message)
    
    @skip_if_erpnext_unavailable
    def test_submit_purchase_order_complete_workflow(self):
        """Test complete PO submission workflow."""
        # Get test PO data
        po_data = self.fixtures.get_test_purchase_order_data(
            company="Test Company CI",
            supplier="Test Supplier Workflow1",
            item_code="TEST-ITEM-WF1"
        )
        
        # Submit PO through workflow
        result = submit_purchase_order_workflow(po_data, self.status_callback)
        
        # Validate result
        self.assertIsNotNone(result)
        self.assertIn('po_name', result)
        self.assertIn('po_data', result)
        self.assertIsInstance(result['po_name'], str)
        self.assertGreater(len(result['po_name']), 0)
        
        # Validate status messages were generated
        self.assertGreater(len(self.status_messages), 0)
        
        # Check that key workflow steps were logged
        status_text = ' '.join(self.status_messages)
        self.assertIn('company', status_text.lower())
        self.assertIn('supplier', status_text.lower())
        self.assertIn('item', status_text.lower())
    
    @skip_if_erpnext_unavailable
    def test_po_workflow_with_multiple_items(self):
        """Test PO workflow with multiple line items."""
        po_data = self.fixtures.get_test_po_with_multiple_items(
            company="Test Company CI",
            supplier="Test Supplier Multi"
        )
        
        result = submit_purchase_order_workflow(po_data, self.status_callback)
        
        self.assertIsNotNone(result)
        self.assertIn('po_name', result)
        
        # Verify all items were processed
        po_details = result['po_data']
        self.assertIn('items', po_details)
        self.assertEqual(len(po_details['items']), 2)
    
    @skip_if_erpnext_unavailable
    def test_po_workflow_creates_missing_supplier(self):
        """Test that workflow auto-creates supplier if it doesn't exist."""
        po_data = self.fixtures.get_test_purchase_order_data(
            company="Test Company CI",
            supplier="Auto Created Supplier WF",
            item_code="TEST-ITEM-AUTO"
        )
        
        result = submit_purchase_order_workflow(po_data, self.status_callback)
        
        self.assertIsNotNone(result)
        
        # Check status messages confirm supplier was created
        status_text = ' '.join(self.status_messages)
        self.assertIn('supplier', status_text.lower())
    
    @skip_if_erpnext_unavailable
    def test_po_workflow_creates_missing_items(self):
        """Test that workflow auto-creates items if they don't exist."""
        po_data = self.fixtures.get_test_purchase_order_data(
            company="Test Company CI",
            supplier="Test Supplier Items",
            item_code="AUTO-CREATED-ITEM-001"
        )
        
        result = submit_purchase_order_workflow(po_data, self.status_callback)
        
        self.assertIsNotNone(result)
        
        # Check that items were processed
        status_text = ' '.join(self.status_messages)
        self.assertIn('item', status_text.lower())


class TestSalesInvoiceWorkflow(unittest.TestCase):
    """Test complete Sales Invoice workflow with real ERPNext."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fixtures = ERPNextFixtures()
        self.status_messages = []
    
    def status_callback(self, message: str):
        """Callback to capture workflow status messages."""
        self.status_messages.append(message)
    
    @skip_if_erpnext_unavailable
    def test_submit_sales_invoice_complete_workflow(self):
        """Test complete sales invoice submission workflow."""
        # Get test invoice data
        invoice_data = self.fixtures.get_test_sales_invoice_data(
            company="Test Company CI",
            customer="Test Customer Workflow1",
            item_code="TEST-ITEM-SI1"
        )
        
        # Submit invoice through workflow
        result = submit_sales_invoice_workflow(invoice_data, self.status_callback)
        
        # Validate result
        self.assertIsNotNone(result)
        self.assertIn('invoice_name', result)
        self.assertIn('invoice_data', result)
        self.assertIsInstance(result['invoice_name'], str)
        self.assertGreater(len(result['invoice_name']), 0)
        
        # Validate status messages were generated
        self.assertGreater(len(self.status_messages), 0)
        
        # Check that key workflow steps were logged
        status_text = ' '.join(self.status_messages)
        self.assertIn('company', status_text.lower())
        self.assertIn('customer', status_text.lower())
        self.assertIn('item', status_text.lower())
    
    @skip_if_erpnext_unavailable
    def test_invoice_workflow_with_multiple_items(self):
        """Test sales invoice workflow with multiple line items."""
        invoice_data = self.fixtures.get_test_invoice_with_multiple_items(
            company="Test Company CI",
            customer="Test Customer Multi"
        )
        
        result = submit_sales_invoice_workflow(invoice_data, self.status_callback)
        
        self.assertIsNotNone(result)
        self.assertIn('invoice_name', result)
        
        # Verify all items were processed
        invoice_details = result['invoice_data']
        self.assertIn('items', invoice_details)
        self.assertEqual(len(invoice_details['items']), 3)
    
    @skip_if_erpnext_unavailable
    def test_invoice_workflow_creates_missing_customer(self):
        """Test that workflow auto-creates customer if it doesn't exist."""
        invoice_data = self.fixtures.get_test_sales_invoice_data(
            company="Test Company CI",
            customer="Auto Created Customer WF",
            item_code="TEST-ITEM-CUST"
        )
        
        result = submit_sales_invoice_workflow(invoice_data, self.status_callback)
        
        self.assertIsNotNone(result)
        
        # Check status messages confirm customer was created
        status_text = ' '.join(self.status_messages)
        self.assertIn('customer', status_text.lower())


class TestWorkflowErrorHandling(unittest.TestCase):
    """Test error handling in workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fixtures = ERPNextFixtures()
        self.status_messages = []
    
    def status_callback(self, message: str):
        """Callback to capture workflow status messages."""
        self.status_messages.append(message)
    
    @skip_if_erpnext_unavailable
    def test_po_workflow_missing_required_fields(self):
        """Test PO workflow with missing required fields raises appropriate error."""
        invalid_po = self.fixtures.get_invalid_po_missing_company()
        
        from app.services.erpnext_service import ValidationError
        
        with self.assertRaises((ValidationError, KeyError)):
            submit_purchase_order_workflow(invalid_po, self.status_callback)
    
    @skip_if_erpnext_unavailable
    def test_invoice_workflow_missing_required_fields(self):
        """Test invoice workflow with missing required fields raises appropriate error."""
        invalid_invoice = self.fixtures.get_invalid_invoice_missing_customer()
        
        from app.services.erpnext_service import ValidationError
        
        with self.assertRaises((ValidationError, KeyError)):
            submit_sales_invoice_workflow(invalid_invoice, self.status_callback)


if __name__ == '__main__':
    unittest.main()
