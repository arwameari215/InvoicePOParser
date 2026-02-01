"""
API Integration Tests - Purchase Order Upload Endpoint.

Tests /upload/po endpoint with various scenarios using Page Object Model.
"""

import unittest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app'))

from tests.integration.helpers.base_test_case import BaseTestCase
from tests.integration.helpers.mock_helpers import MockClaudeResponseBuilder, MockPDFFile
from tests.api.clients.document_upload_client import DocumentUploadClient
from app.main import app
from app.parser_factory import ParserFactory


class TestPOUploadAPI(BaseTestCase):
    """
    Test suite for POST /upload/po endpoint.
    
    Tests:
    - Valid PO upload
    - Invalid file types
    - Missing file handling
    - Currency normalization
    - Date format validation
    - Name cleaning (supplier/company)
    - PO number cleaning
    - Items array handling
    - Extra field removal
    - Response schema matches specification
    - Claude service is called correctly
    """
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        # Reset singleton state between tests
        ParserFactory._claude_service = None
        self.client = TestClient(app)
        self.upload_client = DocumentUploadClient(self.client)
        
        # Create sample PDF
        self.sample_pdf = self.test_data_dir / "api_test_po.pdf"
        MockPDFFile.create_sample_pdf(str(self.sample_pdf), "PO test content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        super().tearDown()
        # Reset singleton
        ParserFactory._claude_service = None
        if self.sample_pdf.exists():
            self.sample_pdf.unlink()
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_valid_po_returns_200(self, mock_claude_service_class):
        """
        Test uploading valid PO PDF returns 200 with complete schema.
        
        Validates:
        - HTTP 200 response
        - All PO fields present
        - Field types are correct
        """
        # Arrange
        mock_service = Mock()
        perfect_response = MockClaudeResponseBuilder.perfect_po_response()
        mock_service.parse_and_validate.return_value = perfect_response
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_po(
            file_data=pdf_bytes,
            filename="test_po.pdf"
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        
        # Verify data structure
        data = response.json()
        self.assertIn('po_number', data)
        self.assertEqual(data['po_number'], "PO-000X")
        self.assertIn('date', data)
        self.assertValidISO8601Date(data['date'])
        self.assertIn('supplier_name', data)
        self.assertIn('company_name', data)
        self.assertIn('delivery_date', data)
        self.assertValidISO8601Date(data['delivery_date'])
        self.assertIn('total_amount', data)
        self.assertNumeric(data['total_amount'])
        self.assertIn('currency', data)
        self.assertValidCurrencyCode(data['currency'])
        self.assertIn('status', data)
        self.assertIn('items', data)
        self.assertIsInstance(data['items'], list)
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_with_txt_file_returns_400(self, mock_claude_service_class):
        """
        Test uploading .txt file returns 400 error.
        
        Validates:
        - HTTP 400 response
        - Error message indicates invalid file type
        """
        # Arrange
        txt_content = b"This is not a PDF"
        
        # Act
        response = self.upload_client.upload_po(
            file_data=txt_content,
            filename="test.txt"
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.upload_client.assert_invalid_file_type_error(response)
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_with_docx_file_returns_400(self, mock_claude_service_class):
        """
        Test uploading .docx file returns 400 error.
        
        Validates:
        - HTTP 400 response
        - Error message indicates invalid file type
        """
        # Arrange
        docx_content = b"Fake DOCX content"
        
        # Act
        response = self.upload_client.upload_po(
            file_data=docx_content,
            filename="test.docx"
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        self.upload_client.assert_invalid_file_type_error(response)
    
    def test_upload_po_without_file_returns_422(self):
        """
        Test uploading without file returns 422 (FastAPI validation error).
        
        Validates:
        - HTTP 422 response for missing required parameter
        - FastAPI automatically handles this validation
        """
        # Act
        response = self.client.post("/upload/po")
        
        # Assert
        self.assertEqual(response.status_code, 422)
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_with_currency_normalization(self, mock_claude_service_class):
        """
        Test that currency symbols are normalized in response.
        
        Validates:
        - € symbol converted to EUR
        - Response contains normalized currency
        """
        # Arrange
        mock_service = Mock()
        response_data = MockClaudeResponseBuilder.perfect_po_response()
        response_data['currency'] = "€"  # Should normalize to EUR
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_po(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['currency'], "EUR")
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_with_date_validation(self, mock_claude_service_class):
        """
        Test that dates are validated to ISO 8601 format.
        
        Validates:
        - Date fields are in YYYY-MM-DD format
        - Both date and delivery_date validated
        """
        # Arrange
        mock_service = Mock()
        response_data = MockClaudeResponseBuilder.perfect_po_response()
        response_data['date'] = "2024-01-24"
        response_data['delivery_date'] = "2024-02-15"
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_po(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertValidISO8601Date(data['date'])
        self.assertValidISO8601Date(data['delivery_date'])
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_with_name_cleaning(self, mock_claude_service_class):
        """
        Test that supplier and company names are cleaned.
        
        Validates:
        - "Supplier: Company Inc" → "Company Inc"
        - "Company: Buyer LLC" → "Buyer LLC"
        """
        # Arrange
        mock_service = Mock()
        response_data = MockClaudeResponseBuilder.po_with_prefix_in_names()
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_po(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Names should be cleaned (no "Supplier:" or "Company:" prefix)
        self.assertNotIn("Supplier:", data['supplier_name'])
        self.assertNotIn("Company:", data['company_name'])
        self.assertEqual(data['supplier_name'], "Test Company")
        self.assertEqual(data['company_name'], "Buyer Corp")
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_with_po_number_cleaning(self, mock_claude_service_class):
        """
        Test that PO numbers are cleaned.
        
        Validates:
        - "Number: PO-123" → "PO-123"
        - Prefix removal
        """
        # Arrange
        mock_service = Mock()
        response_data = MockClaudeResponseBuilder.po_with_prefix_in_names()
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_po(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # PO number should be cleaned (no "Number:" prefix)
        self.assertNotIn("Number:", data['po_number'])
        self.assertEqual(data['po_number'], "PO-123")
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_with_empty_items_array(self, mock_claude_service_class):
        """
        Test PO with empty items array is accepted.
        
        Validates:
        - Empty items array is valid
        - Returns 200 with schema
        """
        # Arrange
        mock_service = Mock()
        import copy
        response_data = copy.deepcopy(MockClaudeResponseBuilder.perfect_po_response())
        response_data['items'] = []
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_po(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['items'], [])
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_po_removes_extra_fields(self, mock_claude_service_class):
        """
        Test that extra AI-hallucinated fields are removed.
        
        Validates:
        - Extra fields not in schema are removed
        - Core fields remain intact
        """
        # Arrange
        mock_service = Mock()
        import copy
        response_data = copy.deepcopy(MockClaudeResponseBuilder.perfect_po_response())
        response_data['extra_field'] = "should be removed"
        response_data['hallucination'] = 12345
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_po(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn('extra_field', data)
        self.assertNotIn('hallucination', data)
        # Core fields should still be present
        self.assertIn('po_number', data)
        self.assertIn('supplier_name', data)
        self.assertIn('company_name', data)


if __name__ == '__main__':
    unittest.main()
