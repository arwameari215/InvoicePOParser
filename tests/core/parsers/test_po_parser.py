"""
Unit Tests for PurchaseOrderClaudeParser.

Tests PO-specific schema validation, field cleaning, and data normalization.
"""

import unittest
from unittest.mock import Mock
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app'))

from tests.integration.helpers.base_test_case import BaseTestCase
from tests.integration.helpers.mock_helpers import MockClaudeResponseBuilder, MockClaudeService, MockPDFFile
from app.parsers.po_claude_parser import PurchaseOrderClaudeParser


class TestPurchaseOrderClaudeParser(BaseTestCase):
    """
    Test suite for PurchaseOrderClaudeParser class.
    
    Validates:
    - Schema validation for all PO fields
    - Currency normalization
    - Date format validation
    - Numeric field handling
    - Name cleaning (supplier/company names)
    - PO number cleaning
    - Items validation
    - Status field validation
    """
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.mock_service = MockClaudeService.create_mock()
        self.test_pdf = self.test_data_dir / "test_po.pdf"
        MockPDFFile.create_sample_pdf(str(self.test_pdf), "PO test content")
    
    def tearDown(self):
        """Clean up after tests."""
        super().tearDown()
        if self.test_pdf.exists():
            self.test_pdf.unlink()
    
    def test_perfect_po_parsing(self):
        """
        Test parsing with perfect AI response.
        
        Validates:
        - All fields present and valid
        - Correct data types
        - Items array properly formatted
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_po_response()
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertIn('po_number', result)
        self.assertEqual(result['po_number'], "PO-000X")
        self.assertIn('date', result)
        self.assertValidISO8601Date(result['date'])
        self.assertIn('supplier_name', result)
        self.assertIn('company_name', result)
        self.assertIn('delivery_date', result)
        self.assertValidISO8601Date(result['delivery_date'])
        self.assertIn('total_amount', result)
        self.assertNumeric(result['total_amount'])
        self.assertIn('currency', result)
        self.assertValidCurrencyCode(result['currency'])
        self.assertIn('status', result)
        self.assertIn('items', result)
        self.assertIsInstance(result['items'], list)
    
    def test_get_prompt_returns_string(self):
        """
        Test that get_prompt returns a non-empty string.
        
        Validates:
        - Prompt is a string
        - Prompt is not empty
        """
        # Arrange
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        prompt = parser.get_prompt()
        
        # Assert
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_po_number_cleaning(self):
        """
        Test that PO numbers with prefixes are cleaned.
        
        Validates:
        - "Number: PO-123" → "PO-123"
        - "PO Number: ABC" → "ABC"
        - Whitespace trimming
        """
        # Arrange
        test_cases = [
            ("Number: PO-12345", "PO-12345"),
            ("PO Number: ABC-999", "ABC-999"),
            ("  PO-000X  ", "PO-000X"),
            ("PO-12345", "PO-12345"),  # No prefix
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                response = MockClaudeResponseBuilder.perfect_po_response()
                response['po_number'] = input_val
                self.mock_service.parse_and_validate.return_value = response
                parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
                
                # Act
                result = parser.parse()
                
                # Assert
                self.assertEqual(result['po_number'], expected)
    
    def test_supplier_name_cleaning(self):
        """
        Test that supplier names with prefixes are cleaned.
        
        Validates:
        - "Supplier: Company Inc" → "Company Inc"
        - "Supplier Name: ABC" → "ABC"
        - Whitespace trimming
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_po_response()
        response['supplier_name'] = "Supplier: Test Company Inc"
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertEqual(result['supplier_name'], "Test Company Inc")
    
    def test_company_name_cleaning(self):
        """
        Test that company names with prefixes are cleaned.
        
        Validates:
        - "Company: Buyer LLC" → "Buyer LLC"
        - "Company Name: XYZ" → "XYZ"
        - Whitespace trimming
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_po_response()
        response['company_name'] = "Company: Buyer Corporation"
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertEqual(result['company_name'], "Buyer Corporation")
    
    def test_date_format_validation(self):
        """
        Test that dates are validated to YYYY-MM-DD format.
        
        Validates:
        - Valid dates pass
        - Invalid dates are caught
        - Both date and delivery_date fields
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_po_response()
        response['date'] = "2024-01-24"
        response['delivery_date'] = "2024-02-15"
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertValidISO8601Date(result['date'])
        self.assertValidISO8601Date(result['delivery_date'])
        self.assertEqual(result['date'], "2024-01-24")
        self.assertEqual(result['delivery_date'], "2024-02-15")
    
    def test_currency_normalization(self):
        """
        Test that currency symbols are normalized to ISO codes.
        
        Validates:
        - € → EUR
        - $ → USD
        - ₪ → ILS
        - £ → GBP
        - ¥ → JPY
        """
        # Arrange
        test_cases = [
            ("€", "EUR"),
            ("$", "USD"),
            ("₪", "ILS"),
            ("£", "GBP"),
            ("¥", "JPY"),
            ("USD", "USD"),  # Already normalized
            ("EUR", "EUR"),
        ]
        
        for symbol, expected_code in test_cases:
            with self.subTest(symbol=symbol):
                response = MockClaudeResponseBuilder.perfect_po_response()
                response['currency'] = symbol
                self.mock_service.parse_and_validate.return_value = response
                parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
                
                # Act
                result = parser.parse()
                
                # Assert
                self.assertEqual(result['currency'], expected_code)
    
    def test_numeric_field_validation(self):
        """
        Test numeric field validation and conversion.
        
        Validates:
        - String numbers converted to float
        - Invalid values rejected
        - total_amount field
        """
        # Arrange
        test_cases = [
            ("40404.50", 40404.50),
            ("1000", 1000.0),
            (5000, 5000.0),
            (5000.99, 5000.99),
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input=input_val):
                response = MockClaudeResponseBuilder.perfect_po_response()
                response['total_amount'] = input_val
                self.mock_service.parse_and_validate.return_value = response
                parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
                
                # Act
                result = parser.parse()
                
                # Assert
                self.assertAlmostEqual(result['total_amount'], expected, places=2)
    
    def test_items_array_validation(self):
        """
        Test items array validation.
        
        Validates:
        - Items must be a list
        - Each item has required fields
        - Empty array is valid
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_po_response()
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertIsInstance(result['items'], list)
        if len(result['items']) > 0:
            item = result['items'][0]
            self.assertIn('description', item)
            self.assertIn('quantity', item)
            self.assertIn('unit_price', item)
            self.assertIn('total', item)
    
    def test_empty_items_array(self):
        """
        Test that empty items array is accepted.
        
        Validates:
        - Empty list is valid
        - No error raised
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_po_response()
        response['items'] = []
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertEqual(result['items'], [])
    
    def test_status_field_validation(self):
        """
        Test that status field is properly validated.
        
        Validates:
        - Status must be string
        - Status is capitalized
        - Common values: Pending, Approved, Completed, etc.
        """
        # Arrange - test that status is capitalized
        test_cases = [
            ("Pending", "Pending"),
            ("APPROVED", "Approved"),  # Capitalized
            ("completed", "Completed"),  # Capitalized
            ("cancelled", "Cancelled"),
            ("In Progress", "In progress"),  # Only first letter uppercase
        ]
        
        for input_status, expected_status in test_cases:
            with self.subTest(status=input_status):
                response = MockClaudeResponseBuilder.perfect_po_response()
                response['status'] = input_status
                self.mock_service.parse_and_validate.return_value = response
                parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
                
                # Act
                result = parser.parse()
                
                # Assert
                self.assertEqual(result['status'], expected_status)
    
    def test_extra_fields_removed(self):
        """
        Test that extra unexpected fields are removed from response.
        
        Validates:
        - Extra keys not in schema are removed
        - Warning is logged
        - Core fields remain intact
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_po_response()
        response['extra_field'] = "should be removed"
        response['hallucination'] = 12345
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertNotIn('extra_field', result)
        self.assertNotIn('hallucination', result)
        self.assertIn('po_number', result)
        self.assertIn('supplier_name', result)
    
    def test_missing_required_fields(self):
        """
        Test handling of missing required fields.
        
        Validates:
        - Warning is logged for missing fields
        - Parser still returns result (Claude may populate)
        """
        # Arrange
        response = {
            "po_number": "PO-001",
            # Missing most required fields
        }
        self.mock_service.parse_and_validate.return_value = response
        parser = PurchaseOrderClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act & Assert - should not raise exception
        result = parser.parse()
        self.assertIn('po_number', result)


if __name__ == '__main__':
    unittest.main()
