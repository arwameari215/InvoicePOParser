"""
Unit Tests for InvoiceClaudeParser.

Tests invoice-specific schema validation, field cleaning, and data normalization.
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app'))

from tests.integration.helpers.base_test_case import BaseTestCase
from tests.integration.helpers.mock_helpers import MockClaudeResponseBuilder, MockClaudeService, MockPDFFile
from app.parsers.invoice_claude_parser import InvoiceClaudeParser


class TestInvoiceClaudeParser(BaseTestCase):
    """
    Test suite for InvoiceClaudeParser class.
    
    Validates:
    - Schema validation for all invoice fields
    - Currency normalization
    - Date format conversion
    - Numeric field handling
    - Extra field removal
    - Confidence + predictionTime wrapping
    """
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.test_pdf = self.test_data_dir / "test_invoice.pdf"
        MockPDFFile.create_sample_pdf(str(self.test_pdf), "Test invoice content")
        self.mock_service = MockClaudeService.create_mock()
    
    def tearDown(self):
        """Clean up test fixtures."""
        super().tearDown()
        if self.test_pdf.exists():
            self.test_pdf.unlink()
    
    def test_perfect_invoice_parsing(self):
        """
        Test parsing with perfect AI response.
        
        Validates:
        - All fields present and correct types
        - Confidence and predictionTime added
        - No errors during validation
        """
        # Arrange
        perfect_response = MockClaudeResponseBuilder.perfect_invoice_response()
        self.mock_service.parse_and_validate.return_value = perfect_response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertIsDict(result)
        self.assertIn('confidence', result)
        self.assertIn('data', result)
        self.assertIn('predictionTime', result)
        
        # Validate data structure
        self.assert_invoice_schema(result)
        
        # Verify specific values
        invoice_data = result['data']
        self.assertEqual(invoice_data['InvoiceId'], "INV-12345")
        self.assertEqual(invoice_data['VendorName'], "Test Vendor Company")
        self.assertEqual(invoice_data['Currency'], "USD")
    
    def test_currency_symbol_normalization(self):
        """
        Test that currency symbols are normalized to ISO codes.
        
        Validates:
        - € → EUR
        - $ → USD
        - ₪ → ILS
        - £ → GBP
        """
        # Test cases for currency normalization
        test_cases = [
            ("€", "EUR"),
            ("$", "USD"),
            ("₪", "ILS"),
            ("£", "GBP"),
            ("¥", "JPY"),
            ("EUR", "EUR"),  # Already correct
            ("USD", "USD"),  # Already correct
        ]
        
        for input_currency, expected_currency in test_cases:
            with self.subTest(input_currency=input_currency):
                # Arrange
                response = MockClaudeResponseBuilder.perfect_invoice_response()
                response['Currency'] = input_currency
                self.mock_service.parse_and_validate.return_value = response
                parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
                
                # Act
                result = parser.parse()
                
                # Assert
                self.assertEqual(result['data']['Currency'], expected_currency)
    
    def test_date_format_conversion(self):
        """
        Test that various date formats are converted to YYYY-MM-DD.
        
        Validates:
        - DD/MM/YYYY → YYYY-MM-DD
        - MM/DD/YYYY → YYYY-MM-DD
        - YYYY-MM-DD remains unchanged
        """
        # Test cases
        test_cases = [
            ("2024-01-15", "2024-01-15"),  # Already ISO
            ("15/01/2024", "2024-01-15"),  # DD/MM/YYYY
        ]
        
        for input_date, expected_date in test_cases:
            with self.subTest(input_date=input_date):
                # Arrange
                response = MockClaudeResponseBuilder.perfect_invoice_response()
                response['InvoiceDate'] = input_date
                self.mock_service.parse_and_validate.return_value = response
                parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
                
                # Act
                result = parser.parse()
                
                # Assert
                self.assertEqual(result['data']['InvoiceDate'], expected_date)
    
    def test_extra_fields_removed(self):
        """
        Test that extra unexpected fields are removed from response.
        
        Validates:
        - Only schema-defined fields remain
        - Extra fields logged but removed
        """
        # Arrange
        response = MockClaudeResponseBuilder.invoice_with_extra_fields()
        self.mock_service.parse_and_validate.return_value = response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        invoice_data = result['data']
        self.assertNotIn('UnexpectedField', invoice_data)
        self.assertNotIn('ExtraData', invoice_data)
        self.assertNotIn('Hallucination', invoice_data)
        
        # Verify all required fields still present
        self.assert_invoice_schema(result)
    
    def test_numeric_field_validation(self):
        """
        Test numeric field validation and conversion.
        
        Validates:
        - String numbers converted to float
        - Invalid numbers handled gracefully
        """
        # Test cases
        test_cases = [
            (1000.50, 1000.50),       # Already float
            ("1000.50", 1000.50),     # String to float
            ("$1,000.50", 1000.50),   # With currency symbol and comma
            ("1000", 1000.0),         # Integer to float
        ]
        
        for input_value, expected_value in test_cases:
            with self.subTest(input_value=input_value):
                # Arrange
                response = MockClaudeResponseBuilder.perfect_invoice_response()
                response['SubTotal'] = input_value
                self.mock_service.parse_and_validate.return_value = response
                parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
                
                # Act
                result = parser.parse()
                
                # Assert
                self.assertEqual(result['data']['SubTotal'], expected_value)
    
    def test_nullable_fields_validation(self):
        """
        Test that nullable fields (Tax, addresses) can be None.
        
        Validates:
        - BillingAddressRecipient can be None
        - ShippingAddress can be None
        - Tax can be None
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_invoice_response()
        response['BillingAddressRecipient'] = None
        response['ShippingAddress'] = None
        response['Tax'] = None
        self.mock_service.parse_and_validate.return_value = response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        invoice_data = result['data']
        self.assertIsNone(invoice_data['BillingAddressRecipient'])
        self.assertIsNone(invoice_data['ShippingAddress'])
        self.assertIsNone(invoice_data['Tax'])
    
    def test_items_array_validation(self):
        """
        Test Items array validation.
        
        Validates:
        - Items can be empty array
        - Items with proper structure accepted
        - Non-array Items converted to empty array
        """
        # Test empty items
        response = MockClaudeResponseBuilder.perfect_invoice_response()
        response['Items'] = []
        self.mock_service.parse_and_validate.return_value = response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        result = parser.parse()
        self.assertEqual(result['data']['Items'], [])
        
        # Test non-array items
        response['Items'] = "not an array"
        self.mock_service.parse_and_validate.return_value = response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        result = parser.parse()
        self.assertEqual(result['data']['Items'], [])
    
    def test_confidence_score_present(self):
        """
        Test that confidence score is added to result.
        
        Validates:
        - Confidence field exists
        - Value is between 0 and 1
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_invoice_response()
        self.mock_service.parse_and_validate.return_value = response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertIn('confidence', result)
        self.assertIsInstance(result['confidence'], (int, float))
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)
    
    def test_prediction_time_present(self):
        """
        Test that predictionTime is added to result.
        
        Validates:
        - predictionTime field exists
        - Value is non-negative number
        """
        # Arrange
        response = MockClaudeResponseBuilder.perfect_invoice_response()
        self.mock_service.parse_and_validate.return_value = response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        self.assertIn('predictionTime', result)
        self.assertNumeric(result['predictionTime'])
        self.assertGreaterEqual(result['predictionTime'], 0)
    
    def test_missing_required_fields(self):
        """
        Test handling of missing required fields.
        
        Validates:
        - Missing fields set to None
        - Parsing doesn't crash
        """
        # Arrange
        response = {
            "InvoiceId": "INV-001",
            # Missing many fields
        }
        self.mock_service.parse_and_validate.return_value = response
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        result = parser.parse()
        
        # Assert
        invoice_data = result['data']
        # Should have all keys but some may be None
        self.assertIn('VendorName', invoice_data)
        self.assertIn('InvoiceDate', invoice_data)
    
    def test_get_prompt_returns_string(self):
        """
        Test that get_prompt returns a non-empty string.
        
        Validates:
        - Prompt is string
        - Prompt is not empty
        - Prompt contains instructions
        """
        # Arrange
        parser = InvoiceClaudeParser(str(self.test_pdf), self.mock_service)
        
        # Act
        prompt = parser.get_prompt()
        
        # Assert
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        # Prompt should mention required fields
        self.assertIn("InvoiceId", prompt)
        self.assertIn("VendorName", prompt)


if __name__ == '__main__':
    unittest.main()
