"""
Unit Tests for ParserFactory.

Tests factory pattern implementation, parser routing, and singleton service management.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app'))

from tests.integration.helpers.base_test_case import BaseTestCase
from app.parser_factory import ParserFactory
from app.parsers.invoice_claude_parser import InvoiceClaudeParser
from app.parsers.po_claude_parser import PurchaseOrderClaudeParser


class TestParserFactory(BaseTestCase):
    """
    Test suite for ParserFactory class.
    
    Validates:
    - Correct parser routing based on document type
    - Singleton ClaudeService management
    - Error handling for unsupported types
    - Supported types list accuracy
    """
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        # Reset singleton state between tests
        ParserFactory._claude_service = None
        self.sample_pdf_path = self.get_sample_pdf_path("test_factory.pdf")
    
    def tearDown(self):
        """Clean up after tests."""
        super().tearDown()
        ParserFactory._claude_service = None
    
    @patch('app.parser_factory.ClaudeService')
    def test_get_parser_for_invoice(self, mock_claude_service_class):
        """
        Test that factory returns InvoiceClaudeParser for invoice document type.
        
        Validates:
        - Correct parser type returned
        - Parser initialized with correct arguments
        - ClaudeService is created
        """
        # Arrange
        mock_service_instance = Mock()
        mock_claude_service_class.return_value = mock_service_instance
        
        # Act
        parser = ParserFactory.get_parser("invoice", self.sample_pdf_path)
        
        # Assert
        self.assertIsInstance(parser, InvoiceClaudeParser)
        self.assertEqual(parser.file_path, self.sample_pdf_path)
        self.assertEqual(parser.claude_service, mock_service_instance)
        mock_claude_service_class.assert_called_once()
    
    @patch('app.parser_factory.ClaudeService')
    def test_get_parser_for_po(self, mock_claude_service_class):
        """
        Test that factory returns PurchaseOrderClaudeParser for PO document type.
        
        Validates:
        - Correct parser type returned
        - Multiple aliases work (po, purchase_order, purchaseorder)
        """
        # Arrange
        mock_service_instance = Mock()
        mock_claude_service_class.return_value = mock_service_instance
        
        # Test different aliases
        aliases = ["po", "purchase_order", "purchaseorder"]
        
        for alias in aliases:
            with self.subTest(alias=alias):
                # Act
                parser = ParserFactory.get_parser(alias, self.sample_pdf_path)
                
                # Assert
                self.assertIsInstance(parser, PurchaseOrderClaudeParser)
                self.assertEqual(parser.file_path, self.sample_pdf_path)
    
    @patch('app.parser_factory.ClaudeService')
    def test_get_parser_case_insensitive(self, mock_claude_service_class):
        """
        Test that document type matching is case-insensitive.
        
        Validates:
        - INVOICE, Invoice, invoice all work
        - PO, Po, po all work
        """
        # Arrange
        mock_service_instance = Mock()
        mock_claude_service_class.return_value = mock_service_instance
        
        # Test case variations
        test_cases = [
            ("INVOICE", InvoiceClaudeParser),
            ("Invoice", InvoiceClaudeParser),
            ("invoice", InvoiceClaudeParser),
            ("PO", PurchaseOrderClaudeParser),
            ("Po", PurchaseOrderClaudeParser),
            ("po", PurchaseOrderClaudeParser),
        ]
        
        for doc_type, expected_class in test_cases:
            with self.subTest(doc_type=doc_type):
                # Act
                parser = ParserFactory.get_parser(doc_type, self.sample_pdf_path)
                
                # Assert
                self.assertIsInstance(parser, expected_class)
    
    @patch('app.parser_factory.ClaudeService')
    def test_unsupported_document_type_raises_error(self, mock_claude_service_class):
        """
        Test that unsupported document type raises ValueError.
        
        Validates:
        - ValueError raised for unknown type
        - Error message contains helpful information
        """
        # Arrange
        mock_service_instance = Mock()
        mock_claude_service_class.return_value = mock_service_instance
        unsupported_types = ["receipt", "contract", "unknown", ""]
        
        for doc_type in unsupported_types:
            with self.subTest(doc_type=doc_type):
                # Act & Assert
                with self.assertRaises(ValueError) as context:
                    ParserFactory.get_parser(doc_type, self.sample_pdf_path)
                
                # Verify error message mentions supported types
                error_message = str(context.exception)
                self.assertIn("Unsupported", error_message)
                self.assertIn(doc_type, error_message)
    
    @patch('app.parser_factory.ClaudeService')
    def test_singleton_claude_service(self, mock_claude_service_class):
        """
        Test that ClaudeService is a singleton (same instance reused).
        
        Validates:
        - ClaudeService created only once
        - Same instance used for multiple parsers
        """
        # Arrange
        mock_service_instance = Mock()
        mock_claude_service_class.return_value = mock_service_instance
        
        # Act - Create multiple parsers
        parser1 = ParserFactory.get_parser("invoice", self.sample_pdf_path)
        parser2 = ParserFactory.get_parser("po", self.sample_pdf_path)
        parser3 = ParserFactory.get_parser("invoice", self.sample_pdf_path)
        
        # Assert
        # ClaudeService should be instantiated only once
        self.assertEqual(mock_claude_service_class.call_count, 1)
        
        # All parsers should share the same service instance
        self.assertIs(parser1.claude_service, mock_service_instance)
        self.assertIs(parser2.claude_service, mock_service_instance)
        self.assertIs(parser3.claude_service, mock_service_instance)
    
    @patch('app.parser_factory.ClaudeService')
    def test_get_parser_with_whitespace(self, mock_claude_service_class):
        """
        Test that document type is trimmed of whitespace.
        
        Validates:
        - Leading/trailing whitespace handled
        - Parsing still works correctly
        """
        # Arrange
        mock_service_instance = Mock()
        mock_claude_service_class.return_value = mock_service_instance
        
        # Act
        parser1 = ParserFactory.get_parser("  invoice  ", self.sample_pdf_path)
        parser2 = ParserFactory.get_parser("\tpo\n", self.sample_pdf_path)
        
        # Assert
        self.assertIsInstance(parser1, InvoiceClaudeParser)
        self.assertIsInstance(parser2, PurchaseOrderClaudeParser)
    
    def test_get_supported_types(self):
        """
        Test that get_supported_types returns correct list.
        
        Validates:
        - Returns a list
        - Contains expected document types
        - No duplicates
        """
        # Act
        supported_types = ParserFactory.get_supported_types()
        
        # Assert
        self.assertIsInstance(supported_types, list)
        self.assertGreater(len(supported_types), 0)
        
        # Check for expected types
        self.assertIn("invoice", supported_types)
        self.assertIn("po", supported_types)
        self.assertIn("purchase_order", supported_types)
        
        # Verify no duplicates
        self.assertEqual(len(supported_types), len(set(supported_types)))
    
    @patch('app.parser_factory.ClaudeService')
    def test_claude_service_initialization_failure(self, mock_claude_service_class):
        """
        Test handling when ClaudeService initialization fails.
        
        Validates:
        - Exception propagated correctly
        - Factory doesn't swallow initialization errors
        """
        # Arrange
        mock_claude_service_class.side_effect = FileNotFoundError("API key not found")
        
        # Act & Assert
        with self.assertRaises(FileNotFoundError) as context:
            ParserFactory.get_parser("invoice", self.sample_pdf_path)
        
        self.assertIn("API key", str(context.exception))


if __name__ == '__main__':
    unittest.main()
