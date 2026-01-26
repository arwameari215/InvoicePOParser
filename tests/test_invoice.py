"""
Unit tests for Invoice Parser.
"""

import unittest
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.parsers.enhanced_invoice_parser import EnhancedInvoiceParser


class TestInvoiceParser(unittest.TestCase):
    """Test cases for EnhancedInvoiceParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_file_path = "test_invoice.pdf"

    @patch('app.parsers.enhanced_invoice_parser.pdfplumber.open')
    def test_load_file_success(self, mock_pdfplumber_open):
        """Test successful file loading."""
        # Mock PDF object
        mock_pdf = MagicMock()
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 text"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 text"
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdfplumber_open.return_value = mock_pdf

        parser = EnhancedInvoiceParser(self.test_file_path)
        
        with patch.object(parser, 'validate_file_exists', return_value=True):
            parser.load_file()
        
        self.assertIsNotNone(parser.document_data)
        self.assertEqual(len(parser.pages), 2)

    @patch('app.parsers.enhanced_invoice_parser.pdfplumber.open')
    def test_load_file_not_found(self, mock_pdfplumber_open):
        """Test file not found error."""
        parser = EnhancedInvoiceParser("nonexistent.pdf")
        
        with patch.object(parser, 'validate_file_exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                parser.load_file()

    @patch('app.parsers.enhanced_invoice_parser.pdfplumber.open')
    def test_load_empty_pdf(self, mock_pdfplumber_open):
        """Test loading an empty PDF file."""
        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdfplumber_open.return_value = mock_pdf

        parser = EnhancedInvoiceParser(self.test_file_path)
        
        with patch.object(parser, 'validate_file_exists', return_value=True):
            with self.assertRaises(ValueError):
                parser.load_file()

    def test_parse_metadata_with_mock_data(self):
        """Test metadata parsing with mock data."""
        parser = EnhancedInvoiceParser(self.test_file_path)
        
        # Mock page object
        mock_page = Mock()
        parser.raw_text = """
        SuperStore INVOICE
        # 36259
        Date: Jan 25 2026
        Bill To:
        Aaron Bergman
        Ship To:
        1915 Beverly
        Balance Due: $1000.00
        Subtotal: $820.00
        Shipping: $180.00
        """
        
        parser.pages = [mock_page]
        parser.document_data = Mock()
        
        metadata = parser.parse_metadata()
        
        self.assertEqual(metadata["InvoiceId"], "36259")
        self.assertIsNotNone(metadata["InvoiceDate"])
        self.assertIsNotNone(metadata["VendorName"])

    def test_parse_items_with_text(self):
        """Test item parsing from text."""
        parser = EnhancedInvoiceParser(self.test_file_path)
        
        parser.raw_text = """
        Item Quantity Rate Amount
        Xerox 1906 4 $141.76 $567.04
        Paper, Office Supplies
        Subtotal: $567.04
        """
        
        parser.pages = [Mock()]
        parser.document_data = Mock()
        
        items = parser.parse_items()
        
        self.assertGreaterEqual(len(items), 1)
        if len(items) > 0:
            self.assertIn("description", items[0])
            self.assertIn("quantity", items[0])

    def test_parse_number(self):
        """Test number parsing utility."""
        parser = EnhancedInvoiceParser(self.test_file_path)
        
        self.assertEqual(parser._parse_number("100"), 100.0)
        self.assertEqual(parser._parse_number("$1,000.50"), 1000.50)
        self.assertEqual(parser._parse_number("€250"), 250.0)
        self.assertEqual(parser._parse_number(None), 0.0)
        self.assertEqual(parser._parse_number("invalid"), 0.0)

    @patch('app.parsers.enhanced_invoice_parser.pdfplumber.open')
    def test_to_dict(self, mock_pdfplumber_open):
        """Test complete parsing to dictionary."""
        mock_pdf = MagicMock()
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        SuperStore INVOICE
        # 123
        Date: Jan 25 2026
        Bill To:
        Test Company
        Balance Due: $500.00
        Subtotal: $450.00
        Shipping: $50.00
        Item Quantity Rate Amount
        Product X 1 $450 $450
        """
        
        mock_pdf.pages = [mock_page]
        mock_pdfplumber_open.return_value = mock_pdf
        
        parser = EnhancedInvoiceParser(self.test_file_path)
        
        with patch.object(parser, 'validate_file_exists', return_value=True):
            parser.load_file()
            result = parser.to_dict()
        
        self.assertIn("data", result)
        self.assertIn("confidence", result)
        self.assertIn("predictionTime", result)
        self.assertIsInstance(result["data"], dict)


if __name__ == "__main__":
    unittest.main()
