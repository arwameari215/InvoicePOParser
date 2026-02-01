"""
Base Test Case - Common utilities and setup for all tests.

Provides shared functionality, mock helpers, and assertions.
"""

import unittest
import sys
import os
from pathlib import Path
from typing import Dict, Any
import logging

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

# Configure test logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise during tests
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseTestCase(unittest.TestCase):
    """
    Base test case with common utilities and assertions.
    
    All test classes should inherit from this base class.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures."""
        cls.project_root = Path(__file__).parent.parent.parent
        cls.test_data_dir = Path(__file__).parent.parent / "data"
        cls.test_data_dir.mkdir(exist_ok=True)
    
    def setUp(self):
        """Set up test fixtures before each test."""
        pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    # ============= Custom Assertions =============
    
    def assertIsDict(self, obj, msg=None):
        """Assert that object is a dictionary."""
        if not isinstance(obj, dict):
            msg = msg or f"Expected dict, got {type(obj).__name__}"
            raise self.failureException(msg)
    
    def assertHasKeys(self, data: dict, keys: list, msg=None):
        """Assert that dictionary has all specified keys."""
        missing_keys = [k for k in keys if k not in data]
        if missing_keys:
            msg = msg or f"Missing keys: {missing_keys}"
            raise self.failureException(msg)
    
    def assertValidISO8601Date(self, date_str: str, msg=None):
        """Assert that string is valid ISO 8601 date (YYYY-MM-DD)."""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, str(date_str)):
            msg = msg or f"Invalid ISO 8601 date: {date_str}"
            raise self.failureException(msg)
    
    def assertValidCurrencyCode(self, currency: str, msg=None):
        """Assert that currency is valid ISO 4217 code."""
        valid_codes = ['USD', 'EUR', 'ILS', 'GBP', 'JPY', 'CNY', 'INR', 'CAD', 'AUD', 'CHF']
        if currency not in valid_codes:
            msg = msg or f"Invalid currency code: {currency}"
            raise self.failureException(msg)
    
    def assertNumeric(self, value, msg=None):
        """Assert that value is numeric (int or float)."""
        if not isinstance(value, (int, float)):
            msg = msg or f"Expected numeric type, got {type(value).__name__}"
            raise self.failureException(msg)
    
    def assertNullableField(self, value, expected_type=None, msg=None):
        """Assert that field is either None or of expected type."""
        if value is not None and expected_type is not None:
            if not isinstance(value, expected_type):
                msg = msg or f"Expected {expected_type.__name__} or None, got {type(value).__name__}"
                raise self.failureException(msg)
    
    # ============= Helper Methods =============
    
    def get_sample_pdf_path(self, filename: str = "sample.pdf") -> str:
        """
        Get path to sample PDF file.
        
        Args:
            filename: Name of the PDF file.
        
        Returns:
            str: Full path to the PDF file.
        """
        return str(self.test_data_dir / filename)
    
    def create_mock_pdf_bytes(self, content: str = "Mock PDF content") -> bytes:
        """
        Create mock PDF bytes for testing.
        
        Args:
            content: Text content to include.
        
        Returns:
            bytes: Mock PDF file bytes.
        """
        # Minimal valid PDF structure
        pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>
endobj
4 0 obj
<< /Length {len(content)} >>
stream
{content}
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000056 00000 n 
0000000114 00000 n 
0000000183 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
{250 + len(content)}
%%EOF
"""
        return pdf_content.encode('utf-8')
    
    def assert_invoice_schema(self, data: Dict[str, Any]):
        """
        Assert that data matches invoice schema.
        
        Args:
            data: Invoice data dictionary.
        """
        self.assertIsDict(data)
        
        # Check wrapper structure
        self.assertIn('confidence', data)
        self.assertIn('data', data)
        self.assertIn('predictionTime', data)
        
        # Check confidence
        self.assertIsInstance(data['confidence'], (int, float))
        self.assertGreaterEqual(data['confidence'], 0)
        self.assertLessEqual(data['confidence'], 1)
        
        # Check predictionTime
        self.assertNumeric(data['predictionTime'])
        
        # Check data structure
        invoice_data = data['data']
        self.assertIsDict(invoice_data)
        
        # Required fields
        required_fields = [
            'InvoiceId', 'VendorName', 'InvoiceDate', 'BillingAddressRecipient',
            'ShippingAddress', 'SubTotal', 'ShippingCost', 'InvoiceTotal', 
            'Tax', 'Currency', 'Items'
        ]
        self.assertHasKeys(invoice_data, required_fields)
        
        # Validate field types
        if invoice_data.get('InvoiceDate'):
            self.assertValidISO8601Date(invoice_data['InvoiceDate'])
        
        if invoice_data.get('Currency'):
            self.assertValidCurrencyCode(invoice_data['Currency'])
        
        # Numeric fields
        for field in ['SubTotal', 'ShippingCost', 'InvoiceTotal']:
            if invoice_data.get(field) is not None:
                self.assertNumeric(invoice_data[field])
        
        # Items must be list
        self.assertIsInstance(invoice_data['Items'], list)
    
    def assert_po_schema(self, data: Dict[str, Any]):
        """
        Assert that data matches PO schema.
        
        Args:
            data: PO data dictionary.
        """
        self.assertIsDict(data)
        
        # Required fields
        required_fields = [
            'po_number', 'date', 'supplier_name', 'company_name',
            'delivery_date', 'total_amount', 'currency', 'status', 'items'
        ]
        self.assertHasKeys(data, required_fields)
        
        # Validate date fields
        if data.get('date'):
            self.assertValidISO8601Date(data['date'])
        if data.get('delivery_date'):
            self.assertValidISO8601Date(data['delivery_date'])
        
        # Validate currency
        if data.get('currency'):
            self.assertValidCurrencyCode(data['currency'])
        
        # Validate total_amount
        if data.get('total_amount') is not None:
            self.assertNumeric(data['total_amount'])
        
        # Items must be list
        self.assertIsInstance(data['items'], list)
        
        # Validate item structure
        for item in data['items']:
            self.assertIsDict(item)
            item_fields = ['description', 'quantity', 'unit_price', 'total']
            self.assertHasKeys(item, item_fields)
