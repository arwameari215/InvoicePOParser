"""
Unit tests for FastAPI endpoints.
"""

import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
import sys
import os
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for FastAPI endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("endpoints", data)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")

    def test_supported_types(self):
        """Test supported types endpoint."""
        response = self.client.get("/supported-types")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("supported_types", data)
        self.assertIsInstance(data["supported_types"], list)

    def test_upload_invoice_invalid_file_type(self):
        """Test invoice upload with invalid file type."""
        # Create a fake text file
        file_content = b"This is not a PDF"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        response = self.client.post("/upload/invoice", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file type", response.json()["detail"])

    def test_upload_po_invalid_file_type(self):
        """Test PO upload with invalid file type."""
        # Create a fake text file
        file_content = b"This is not a PDF"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        response = self.client.post("/upload/po", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file type", response.json()["detail"])

    @patch('app.main.ParserFactory.get_parser')
    def test_upload_invoice_success(self, mock_get_parser):
        """Test successful invoice upload."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.to_dict.return_value = {
            "metadata": {
                "invoice_number": "INV123",
                "date": "2026-01-25",
                "supplier_name": "Test Supplier",
                "total_amount": 1000.0,
                "tax": 180.0
            },
            "items": [
                {"description": "Item A", "quantity": 2, "unit_price": 100, "total": 200}
            ]
        }
        mock_get_parser.return_value = mock_parser
        
        # Create a fake PDF file
        file_content = b"%PDF-1.4 fake pdf content"
        files = {"file": ("test_invoice.pdf", BytesIO(file_content), "application/pdf")}
        
        response = self.client.post("/upload/invoice", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("metadata", data)
        self.assertIn("items", data)

    @patch('app.main.ParserFactory.get_parser')
    def test_upload_po_success(self, mock_get_parser):
        """Test successful PO upload."""
        # Mock parser
        mock_parser = Mock()
        mock_parser.to_dict.return_value = {
            "metadata": {
                "po_number": "PO123",
                "date": "2026-01-25",
                "supplier_name": "Supplier X",
                "delivery_date": "2026-02-01",
                "total_amount": 5000.0,
                "status": "Pending"
            },
            "items": [
                {"description": "Product A", "quantity": 10, "unit_price": 500, "total": 5000}
            ]
        }
        mock_get_parser.return_value = mock_parser
        
        # Create a fake PDF file
        file_content = b"%PDF-1.4 fake pdf content"
        files = {"file": ("test_po.pdf", BytesIO(file_content), "application/pdf")}
        
        response = self.client.post("/upload/po", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("metadata", data)
        self.assertIn("items", data)


if __name__ == "__main__":
    unittest.main()
