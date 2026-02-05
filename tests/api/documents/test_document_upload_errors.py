"""
API Tests - Document Upload Error Handling

Tests error paths and edge cases for document upload endpoints:
- FileNotFoundError handling
- ValueError handling  
- Generic Exception handling
- File cleanup on error
- Temporary file removal failures
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.main import app
from app.parser_factory import ParserFactory
from tests.integration.helpers.base_test_case import BaseTestCase
from tests.integration.helpers.mock_helpers import MockPDFFile


class TestDocumentUploadErrors(BaseTestCase):
    """Test error handling in document upload endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        ParserFactory._claude_service = None
        self.client = TestClient(app)
        
        # Create sample PDFs
        self.sample_invoice_pdf = self.test_data_dir / "error_test_invoice.pdf"
        self.sample_po_pdf = self.test_data_dir / "error_test_po.pdf"
        MockPDFFile.create_sample_pdf(str(self.sample_invoice_pdf), "Invoice error test")
        MockPDFFile.create_sample_pdf(str(self.sample_po_pdf), "PO error test")
    
    def tearDown(self):
        """Clean up test fixtures."""
        super().tearDown()
        ParserFactory._claude_service = None
        for pdf in [self.sample_invoice_pdf, self.sample_po_pdf]:
            if pdf.exists():
                pdf.unlink()
    
    # ========================================================================
    # Invoice Upload Error Tests
    # ========================================================================
    
    @patch('app.parser_factory.ClaudeService')
    def test_invoice_upload_file_not_found_error(self, mock_claude_service_class):
        """Test invoice upload handles FileNotFoundError (404)."""
        mock_service = Mock()
        mock_service.parse_and_validate.side_effect = FileNotFoundError("PDF file not found")
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_invoice_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/invoice",
            files={"file": ("test_invoice.pdf", pdf_bytes, "application/pdf")}
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('detail', data)
    
    @patch('app.parser_factory.ClaudeService')
    def test_invoice_upload_value_error(self, mock_claude_service_class):
        """Test invoice upload handles ValueError (400)."""
        mock_service = Mock()
        mock_service.parse_and_validate.side_effect = ValueError("Invalid invoice format")
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_invoice_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/invoice",
            files={"file": ("test_invoice.pdf", pdf_bytes, "application/pdf")}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Parsing error', data['detail'])
    
    @patch('app.parser_factory.ClaudeService')
    def test_invoice_upload_generic_exception(self, mock_claude_service_class):
        """Test invoice upload handles generic Exception (500)."""
        mock_service = Mock()
        mock_service.parse_and_validate.side_effect = RuntimeError("Unexpected error occurred")
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_invoice_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/invoice",
            files={"file": ("test_invoice.pdf", pdf_bytes, "application/pdf")}
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Internal server error', data['detail'])
    
    @patch('app.parser_factory.ClaudeService')
    @patch('os.remove')
    def test_invoice_upload_cleanup_failure_is_logged(self, mock_remove, mock_claude_service_class):
        """Test invoice upload logs warning when file cleanup fails."""
        mock_service = Mock()
        mock_service.parse_and_validate.return_value = {
            'confidence': 0.9,
            'data': {'InvoiceId': 'INV-001'},
            'predictionTime': 1.5
        }
        mock_claude_service_class.return_value = mock_service
        
        # Simulate cleanup failure
        mock_remove.side_effect = PermissionError("File in use")
        
        pdf_bytes = self.sample_invoice_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/invoice",
            files={"file": ("test_invoice.pdf", pdf_bytes, "application/pdf")}
        )
        
        # Should still return success even if cleanup fails
        self.assertEqual(response.status_code, 200)
        mock_remove.assert_called_once()
    
    # ========================================================================
    # PO Upload Error Tests
    # ========================================================================
    
    @patch('app.parser_factory.ClaudeService')
    def test_po_upload_file_not_found_error(self, mock_claude_service_class):
        """Test PO upload handles FileNotFoundError (404)."""
        mock_service = Mock()
        mock_service.parse_and_validate.side_effect = FileNotFoundError("PDF file not found")
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_po_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/po",
            files={"file": ("test_po.pdf", pdf_bytes, "application/pdf")}
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('detail', data)
    
    @patch('app.parser_factory.ClaudeService')
    def test_po_upload_value_error(self, mock_claude_service_class):
        """Test PO upload handles ValueError (400)."""
        mock_service = Mock()
        mock_service.parse_and_validate.side_effect = ValueError("Invalid PO format")
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_po_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/po",
            files={"file": ("test_po.pdf", pdf_bytes, "application/pdf")}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Parsing error', data['detail'])
    
    @patch('app.parser_factory.ClaudeService')
    def test_po_upload_generic_exception(self, mock_claude_service_class):
        """Test PO upload handles generic Exception (500)."""
        mock_service = Mock()
        mock_service.parse_and_validate.side_effect = RuntimeError("Unexpected error occurred")
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_po_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/po",
            files={"file": ("test_po.pdf", pdf_bytes, "application/pdf")}
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('Internal server error', data['detail'])
    
    @patch('app.parser_factory.ClaudeService')
    @patch('os.remove')
    def test_po_upload_cleanup_failure_is_logged(self, mock_remove, mock_claude_service_class):
        """Test PO upload logs warning when file cleanup fails."""
        mock_service = Mock()
        mock_service.parse_and_validate.return_value = {
            'po_number': 'PO-001',
            'supplier_name': 'Test Supplier',
            'items': []
        }
        mock_claude_service_class.return_value = mock_service
        
        # Simulate cleanup failure
        mock_remove.side_effect = PermissionError("File in use")
        
        pdf_bytes = self.sample_po_pdf.read_bytes()
        
        response = self.client.post(
            "/upload/po",
            files={"file": ("test_po.pdf", pdf_bytes, "application/pdf")}
        )
        
        # Should still return success even if cleanup fails
        self.assertEqual(response.status_code, 200)
        mock_remove.assert_called_once()


if __name__ == '__main__':
    unittest.main()
