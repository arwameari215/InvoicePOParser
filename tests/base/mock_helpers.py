"""
Mock Helpers - Utilities for creating mock AI responses and services.

Provides builders for various mock scenarios.
"""

from typing import Dict, Any, Optional, List
from unittest.mock import Mock, MagicMock
import json
import copy


class MockClaudeResponseBuilder:
    """
    Builder for creating mock Claude AI responses.
    
    Supports various scenarios: perfect, missing fields, wrong types, etc.
    """
    
    @staticmethod
    def perfect_invoice_response() -> Dict[str, Any]:
        """
        Create a perfect invoice response with all fields.
        
        Returns:
            Dict: Complete valid invoice data.
        """
        return {
            "InvoiceId": "INV-12345",
            "VendorName": "Test Vendor Company",
            "InvoiceDate": "2024-01-15",
            "BillingAddressRecipient": "John Doe",
            "ShippingAddress": "123 Main St, City, Country",
            "SubTotal": 1000.50,
            "ShippingCost": 25.00,
            "InvoiceTotal": 1195.60,
            "Tax": 170.10,
            "Currency": "USD",
            "Items": [
                {
                    "description": "Product A",
                    "quantity": 2,
                    "unit_price": 500.25,
                    "total": 1000.50
                }
            ]
        }
    
    @staticmethod
    def perfect_po_response() -> Dict[str, Any]:
        """
        Create a perfect PO response with all fields.
        
        Returns:
            Dict: Complete valid PO data.
        """
        return {
            "po_number": "PO-000X",
            "date": "2024-01-24",
            "supplier_name": "Supplier Company Inc",
            "company_name": "Buyer Company LLC",
            "delivery_date": "2024-01-30",
            "total_amount": 40404.00,
            "currency": "EUR",
            "status": "Pending",
            "items": [
                {
                    "description": "Product SKU005",
                    "quantity": 182.0,
                    "unit_price": 222.0,
                    "total": 40404.0
                }
            ]
        }
    
    @staticmethod
    def invoice_with_missing_fields() -> Dict[str, Any]:
        """
        Invoice response with some required fields missing.
        
        Returns:
            Dict: Incomplete invoice data.
        """
        return {
            "InvoiceId": "INV-001",
            "VendorName": "Test Vendor",
            # Missing InvoiceDate, addresses, amounts
        }
    
    @staticmethod
    def invoice_with_wrong_types() -> Dict[str, Any]:
        """
        Invoice response with incorrect field types.
        
        Returns:
            Dict: Invoice data with type errors.
        """
        return {
            "InvoiceId": 12345,  # Should be string
            "VendorName": "Test Vendor",
            "InvoiceDate": "2024-01-15",
            "BillingAddressRecipient": None,
            "ShippingAddress": None,
            "SubTotal": "not_a_number",  # Should be float
            "ShippingCost": "25.00",  # String instead of float
            "InvoiceTotal": 1195.60,
            "Tax": None,
            "Currency": "USD",
            "Items": "not_a_list"  # Should be list
        }
    
    @staticmethod
    def invoice_with_extra_fields() -> Dict[str, Any]:
        """
        Invoice response with extra unexpected fields.
        
        Returns:
            Dict: Invoice data with extra fields.
        """
        response = copy.deepcopy(MockClaudeResponseBuilder.perfect_invoice_response())
        response["UnexpectedField"] = "should be removed"
        response["ExtraData"] = 12345
        response["Hallucination"] = {"nested": "data"}
        return response
    
    @staticmethod
    def invoice_with_currency_symbol() -> Dict[str, Any]:
        """
        Invoice with currency as symbol instead of code.
        
        Returns:
            Dict: Invoice with currency symbol.
        """
        response = copy.deepcopy(MockClaudeResponseBuilder.perfect_invoice_response())
        response["Currency"] = "€"  # Should normalize to EUR
        return response
    
    @staticmethod
    def invoice_with_alternate_date_format() -> Dict[str, Any]:
        """
        Invoice with date in DD/MM/YYYY format.
        
        Returns:
            Dict: Invoice with non-ISO date.
        """
        response = copy.deepcopy(MockClaudeResponseBuilder.perfect_invoice_response())
        response["InvoiceDate"] = "15/01/2024"  # Should convert to 2024-01-15
        return response
    
    @staticmethod
    def po_with_prefix_in_names() -> Dict[str, Any]:
        """
        PO with prefixes in supplier/company names.
        
        Returns:
            Dict: PO with name prefixes.
        """
        response = copy.deepcopy(MockClaudeResponseBuilder.perfect_po_response())
        response["supplier_name"] = "Supplier: Test Company"
        response["company_name"] = "Company: Buyer Corp"
        response["po_number"] = "Number: PO-123"
        return response
    
    @staticmethod
    def empty_items_array() -> List:
        """
        Empty items array.
        
        Returns:
            List: Empty list.
        """
        return []
    
    @staticmethod
    def invalid_json_string() -> str:
        """
        Invalid JSON string (malformed).
        
        Returns:
            str: Malformed JSON.
        """
        return '{"InvoiceId": "INV-001", "invalid": }'
    
    @staticmethod
    def json_with_markdown_fences() -> str:
        """
        Valid JSON wrapped in markdown code fences.
        
        Returns:
            str: JSON with markdown.
        """
        invoice = MockClaudeResponseBuilder.perfect_invoice_response()
        return f"```json\n{json.dumps(invoice)}\n```"


class MockClaudeService:
    """
    Mock ClaudeService for testing without API calls.
    """
    
    @staticmethod
    def create_mock(return_value: Optional[Dict[str, Any]] = None) -> Mock:
        """
        Create a mock ClaudeService with configurable return value.
        
        Args:
            return_value: Data to return from parse_and_validate().
        
        Returns:
            Mock: Configured mock service.
        """
        mock_service = Mock()
        mock_service.parse_and_validate = Mock(
            return_value=return_value or MockClaudeResponseBuilder.perfect_invoice_response()
        )
        mock_service.parse_document = Mock(return_value=json.dumps(return_value or {}))
        mock_service.encode_pdf_to_base64 = Mock(return_value="base64_encoded_pdf")
        mock_service.clean_json_response = Mock(side_effect=lambda x: x)
        mock_service.parse_json = Mock(side_effect=json.loads)
        return mock_service
    
    @staticmethod
    def create_mock_with_exception(exception: Exception) -> Mock:
        """
        Create a mock that raises an exception.
        
        Args:
            exception: Exception to raise.
        
        Returns:
            Mock: Mock that raises exception.
        """
        mock_service = Mock()
        mock_service.parse_and_validate = Mock(side_effect=exception)
        return mock_service


class MockAnthropicClient:
    """
    Mock Anthropic client for testing ClaudeService.
    """
    
    @staticmethod
    def create_mock(response_text: str) -> Mock:
        """
        Create a mock Anthropic client.
        
        Args:
            response_text: Text to return from API call.
        
        Returns:
            Mock: Configured Anthropic client mock.
        """
        mock_client = Mock()
        
        # Mock the message response structure
        mock_message = Mock()
        mock_content = Mock()
        mock_content.text = response_text
        mock_message.content = [mock_content]
        
        mock_client.messages.create = Mock(return_value=mock_message)
        
        return mock_client


class MockPDFFile:
    """
    Mock PDF file for testing file operations.
    """
    
    @staticmethod
    def create_sample_pdf(output_path: str, content: str = "Sample PDF content"):
        """
        Create a minimal valid PDF file for testing.
        
        Args:
            output_path: Path where to save the PDF.
            content: Text content to include.
        """
        from pathlib import Path
        
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
        Path(output_path).write_text(pdf_content)
    
    @staticmethod
    def create_empty_pdf(output_path: str):
        """
        Create an empty PDF file.
        
        Args:
            output_path: Path where to save the PDF.
        """
        from pathlib import Path
        Path(output_path).write_bytes(b'%PDF-1.4\n%%EOF')
    
    @staticmethod
    def create_corrupted_file(output_path: str):
        """
        Create a corrupted/invalid file.
        
        Args:
            output_path: Path where to save the file.
        """
        from pathlib import Path
        Path(output_path).write_bytes(b'This is not a valid PDF')
