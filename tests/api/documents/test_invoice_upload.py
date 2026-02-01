"""
API Integration Tests - Invoice Upload Endpoint.

Tests /upload/invoice endpoint with various scenarios using Page Object Model.
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


class TestInvoiceUploadAPI(BaseTestCase):
    """
    Test suite for POST /upload/invoice endpoint.
    
    Validates:
    - Valid PDF upload returns 200 with correct schema
    - Invalid file types return 400
    - Missing file returns 422
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
        self.sample_pdf = self.test_data_dir / "api_test_invoice.pdf"
        MockPDFFile.create_sample_pdf(str(self.sample_pdf), "Invoice test content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        super().tearDown()
        # Reset singleton
        ParserFactory._claude_service = None
        if self.sample_pdf.exists():
            self.sample_pdf.unlink()
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_valid_invoice_returns_200(self, mock_claude_service_class):
        """
        Test uploading valid invoice PDF returns 200 with complete schema.
        
        Validates:
        - HTTP 200 response
        - Response contains confidence, data, predictionTime
        - All invoice fields present
        - Field types are correct
        """
        # Arrange
        mock_service = Mock()
        perfect_response = MockClaudeResponseBuilder.perfect_invoice_response()
        mock_service.parse_and_validate.return_value = perfect_response
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_invoice(
            file_data=pdf_bytes,
            filename="test_invoice.pdf"
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.upload_client.assert_invoice_schema(response)
        
        # Verify data
        data = response.json()
        self.assertEqual(data['data']['InvoiceId'], "INV-12345")
        self.assertEqual(data['data']['VendorName'], "Test Vendor Company")
        self.assertIn('Currency', data['data'])
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_with_txt_file_returns_400(self, mock_claude_service_class):
        """
        Test uploading .txt file returns 400 error.
        
        Validates:
        - HTTP 400 response
        - Error message mentions PDF requirement
        """
        # Arrange
        mock_service = Mock()
        mock_claude_service_class.return_value = mock_service
        
        txt_content = b"This is not a PDF file"
        
        # Act
        response = self.upload_client.upload_invalid_file_type_invoice(
            file_data=txt_content,
            filename="test.txt"
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('detail', data)
        self.assertIn('pdf', data['detail'].lower())
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_with_docx_file_returns_400(self, mock_claude_service_class):
        """
        Test uploading .docx file returns 400 error.
        
        Validates:
        - HTTP 400 response
        - Only PDF files accepted
        """
        # Arrange
        mock_service = Mock()
        mock_claude_service_class.return_value = mock_service
        
        # Minimal docx structure
        docx_content = b"PK\x03\x04fake docx content"
        
        # Act
        response = self.upload_client.upload_invalid_file_type_invoice(
            file_data=docx_content,
            filename="test.docx"
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
    
    def test_upload_invoice_without_file_returns_422(self):
        """
        Test uploading without file returns 422 (FastAPI validation error).
        
        Validates:
        - HTTP 422 response
        - Missing required field error
        """
        # Act
        response = self.upload_client.upload_invoice_without_file()
        
        # Assert
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn('detail', data)
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_with_currency_normalization(self, mock_claude_service_class):
        """
        Test that currency symbols are normalized in response.
        
        Validates:
        - Currency symbols converted to ISO codes
        - Response contains normalized currency
        """
        # Arrange
        mock_service = Mock()
        invoice_with_symbol = MockClaudeResponseBuilder.invoice_with_currency_symbol()
        mock_service.parse_and_validate.return_value = invoice_with_symbol
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_invoice(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # € should be normalized to EUR
        self.assertEqual(data['data']['Currency'], "EUR")
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_with_date_format_conversion(self, mock_claude_service_class):
        """
        Test that date formats are converted to ISO 8601.
        
        Validates:
        - DD/MM/YYYY converted to YYYY-MM-DD
        - Response contains ISO date format
        """
        # Arrange
        mock_service = Mock()
        invoice_with_alt_date = MockClaudeResponseBuilder.invoice_with_alternate_date_format()
        mock_service.parse_and_validate.return_value = invoice_with_alt_date
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_invoice(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertValidISO8601Date(data['data']['InvoiceDate'])
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_with_empty_items_array(self, mock_claude_service_class):
        """
        Test invoice with empty Items array is accepted.
        
        Validates:
        - Empty Items array is valid
        - Returns 200 with schema
        """
        # Arrange
        mock_service = Mock()
        response_data = MockClaudeResponseBuilder.perfect_invoice_response()
        response_data['Items'] = []
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_invoice(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['data']['Items'], [])
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_with_nullable_fields_as_none(self, mock_claude_service_class):
        """
        Test that nullable fields (Tax, addresses) can be None.
        
        Validates:
        - BillingAddressRecipient, ShippingAddress, Tax can be None
        - Response still valid
        """
        # Arrange
        mock_service = Mock()
        response_data = MockClaudeResponseBuilder.perfect_invoice_response()
        response_data['BillingAddressRecipient'] = None
        response_data['ShippingAddress'] = None
        response_data['Tax'] = None
        mock_service.parse_and_validate.return_value = response_data
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_invoice(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data['data']['BillingAddressRecipient'])
        self.assertIsNone(data['data']['ShippingAddress'])
        self.assertIsNone(data['data']['Tax'])
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_removes_extra_fields(self, mock_claude_service_class):
        """
        Test that extra AI-hallucinated fields are removed.
        
        Validates:
        - Only schema-defined fields in response
        - Extra fields stripped
        """
        # Arrange
        mock_service = Mock()
        response_with_extra = MockClaudeResponseBuilder.invoice_with_extra_fields()
        mock_service.parse_and_validate.return_value = response_with_extra
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_invoice(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        invoice_data = data['data']
        
        # Extra fields should not be present
        self.assertNotIn('UnexpectedField', invoice_data)
        self.assertNotIn('ExtraData', invoice_data)
        self.assertNotIn('Hallucination', invoice_data)
    
    @patch('app.parser_factory.ClaudeService')
    def test_upload_invoice_response_time_tracking(self, mock_claude_service_class):
        """
        Test that predictionTime is tracked and returned.
        
        Validates:
        - predictionTime field exists
        - Value is positive number
        """
        # Arrange
        mock_service = Mock()
        perfect_response = MockClaudeResponseBuilder.perfect_invoice_response()
        mock_service.parse_and_validate.return_value = perfect_response
        mock_claude_service_class.return_value = mock_service
        
        pdf_bytes = self.sample_pdf.read_bytes()
        
        # Act
        response = self.upload_client.upload_invoice(file_data=pdf_bytes)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('predictionTime', data)
        self.assertNumeric(data['predictionTime'])
        self.assertGreaterEqual(data['predictionTime'], 0)


if __name__ == '__main__':
    unittest.main()
