"""
Unit tests for Purchase Order Parser.
"""

import unittest
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.parsers.po_parser import PurchaseOrderParser


class TestPurchaseOrderParser(unittest.TestCase):
    """Test cases for PurchaseOrderParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_file_path = "test_po.pdf"

    @patch('app.parsers.po_parser.pdfplumber.open')
    def test_load_file_success(self, mock_pdfplumber_open):
        """Test successful file loading."""
        # Mock PDF object
        mock_pdf = MagicMock()
        mock_pdf.pages = [Mock(), Mock()]
        mock_pdfplumber_open.return_value = mock_pdf

        parser = PurchaseOrderParser(self.test_file_path)
        
        with patch.object(parser, 'validate_file_exists', return_value=True):
            parser.load_file()
        
        self.assertIsNotNone(parser.document_data)
        self.assertEqual(len(parser.pages), 2)

    @patch('app.parsers.po_parser.pdfplumber.open')
    def test_load_file_not_found(self, mock_pdfplumber_open):
        """Test file not found error."""
        parser = PurchaseOrderParser("nonexistent.pdf")
        
        with patch.object(parser, 'validate_file_exists', return_value=False):
            with self.assertRaises(FileNotFoundError):
                parser.load_file()

    @patch('app.parsers.po_parser.pdfplumber.open')
    def test_load_empty_pdf(self, mock_pdfplumber_open):
        """Test loading an empty PDF file."""
        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdfplumber_open.return_value = mock_pdf

        parser = PurchaseOrderParser(self.test_file_path)
        
        with patch.object(parser, 'validate_file_exists', return_value=True):
            with self.assertRaises(ValueError):
                parser.load_file()

    def test_parse_metadata_with_mock_data(self):
        """Test metadata parsing with mock data."""
        parser = PurchaseOrderParser(self.test_file_path)
        
        # Mock page object
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Purchase Order PO123
        Date: 2026-01-25
        Supplier: Supplier X
        Delivery Date: 2026-02-01
        Total: $5000.00
        Status: Pending
        """
        
        parser.pages = [mock_page]
        parser.document_data = Mock()
        
        metadata = parser.parse_metadata()
        
        self.assertEqual(metadata["po_number"], "PO123")
        self.assertEqual(metadata["date"], "2026-01-25")
        self.assertEqual(metadata["supplier_name"], "Supplier X")
        self.assertEqual(metadata["delivery_date"], "2026-02-01")
        self.assertEqual(metadata["total_amount"], 5000.0)
        self.assertEqual(metadata["status"], "Pending")

    def test_parse_items_with_table(self):
        """Test item parsing with table data."""
        parser = PurchaseOrderParser(self.test_file_path)
        
        # Mock page with table
        mock_page = Mock()
        mock_table = [
            ["Description", "Quantity", "Unit Price", "Total"],
            ["Product A", "10", "500", "5000"],
            ["Product B", "5", "200", "1000"]
        ]
        mock_page.extract_tables.return_value = [mock_table]
        
        parser.pages = [mock_page]
        parser.document_data = Mock()
        
        items = parser.parse_items()
        
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["description"], "Product A")
        self.assertEqual(items[0]["quantity"], 10.0)
        self.assertEqual(items[0]["unit_price"], 500.0)
        self.assertEqual(items[0]["total"], 5000.0)

    def test_parse_number(self):
        """Test number parsing utility."""
        parser = PurchaseOrderParser(self.test_file_path)
        
        self.assertEqual(parser._parse_number("100"), 100.0)
        self.assertEqual(parser._parse_number("$1,000.50"), 1000.50)
        self.assertEqual(parser._parse_number("€250"), 250.0)
        self.assertEqual(parser._parse_number(None), 0.0)
        self.assertEqual(parser._parse_number("invalid"), 0.0)

    def test_find_column_index(self):
        """Test column index finding."""
        parser = PurchaseOrderParser(self.test_file_path)
        
        header = ["description", "qty", "price", "total"]
        
        self.assertEqual(parser._find_column_index(header, ["description", "item"]), 0)
        self.assertEqual(parser._find_column_index(header, ["quantity", "qty"]), 1)
        self.assertIsNone(parser._find_column_index(header, ["invalid"]))

    @patch('app.parsers.po_parser.pdfplumber.open')
    def test_to_dict(self, mock_pdfplumber_open):
        """Test complete parsing to dictionary."""
        mock_pdf = MagicMock()
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Purchase Order PO456
        Date: 2026-01-25
        Supplier: ABC Corp
        Delivery Date: 2026-02-15
        Total: $2500
        Status: Approved
        """
        mock_page.extract_tables.return_value = [[
            ["Description", "Quantity", "Price", "Total"],
            ["Widget", "25", "100", "2500"]
        ]]
        
        mock_pdf.pages = [mock_page]
        mock_pdfplumber_open.return_value = mock_pdf
        
        parser = PurchaseOrderParser(self.test_file_path)
        
        with patch.object(parser, 'validate_file_exists', return_value=True):
            parser.load_file()
            result = parser.to_dict()
        
        self.assertIn("metadata", result)
        self.assertIn("items", result)
        self.assertIsInstance(result["metadata"], dict)
        self.assertIsInstance(result["items"], list)

    def test_default_status(self):
        """Test default status is 'Pending' when not found."""
        parser = PurchaseOrderParser(self.test_file_path)
        
        mock_page = Mock()
        mock_page.extract_text.return_value = """
        Purchase Order PO789
        Date: 2026-01-25
        """
        
        parser.pages = [mock_page]
        parser.document_data = Mock()
        
        metadata = parser.parse_metadata()
        
        self.assertEqual(metadata["status"], "Pending")


if __name__ == "__main__":
    unittest.main()
