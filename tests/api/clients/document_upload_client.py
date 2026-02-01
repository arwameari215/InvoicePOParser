"""
Document Upload API Client - Page Object for document upload endpoints.

Encapsulates document upload operations with various scenarios.
"""

from .base_api_client import BaseAPIClient
from typing import Dict, Any, Optional
from io import BytesIO


class DocumentUploadClient(BaseAPIClient):
    """
    API client for document upload endpoints.
    
    Provides methods for testing invoice and PO upload endpoints.
    """
    
    def upload_invoice(
        self, 
        file_data: bytes, 
        filename: str = "test_invoice.pdf",
        content_type: str = "application/pdf"
    ):
        """
        Upload an invoice PDF file.
        
        Args:
            file_data: PDF file bytes.
            filename: Name of the file.
            content_type: MIME type of the file.
        
        Returns:
            Response object.
        """
        files = {"file": (filename, BytesIO(file_data), content_type)}
        return self.post("/upload/invoice", files=files)
    
    def upload_po(
        self, 
        file_data: bytes, 
        filename: str = "test_po.pdf",
        content_type: str = "application/pdf"
    ):
        """
        Upload a purchase order PDF file.
        
        Args:
            file_data: PDF file bytes.
            filename: Name of the file.
            content_type: MIME type of the file.
        
        Returns:
            Response object.
        """
        files = {"file": (filename, BytesIO(file_data), content_type)}
        return self.post("/upload/po", files=files)
    
    def upload_invoice_without_file(self):
        """
        Attempt to upload invoice without file (should fail).
        
        Returns:
            Response object.
        """
        return self.post("/upload/invoice")
    
    def upload_po_without_file(self):
        """
        Attempt to upload PO without file (should fail).
        
        Returns:
            Response object.
        """
        return self.post("/upload/po")
    
    def upload_invalid_file_type_invoice(self, file_data: bytes, filename: str = "test.txt"):
        """
        Upload non-PDF file to invoice endpoint (should fail).
        
        Args:
            file_data: File bytes.
            filename: Name of the file.
        
        Returns:
            Response object.
        """
        files = {"file": (filename, BytesIO(file_data), "text/plain")}
        return self.post("/upload/invoice", files=files)
    
    def upload_invalid_file_type_po(self, file_data: bytes, filename: str = "test.txt"):
        """
        Upload non-PDF file to PO endpoint (should fail).
        
        Args:
            file_data: File bytes.
            filename: Name of the file.
        
        Returns:
            Response object.
        """
        files = {"file": (filename, BytesIO(file_data), "text/plain")}
        return self.post("/upload/po", files=files)
    
    def assert_invoice_schema(self, response):
        """
        Assert that invoice response matches expected schema.
        
        Args:
            response: Response from invoice upload endpoint.
        
        Raises:
            AssertionError: If schema doesn't match.
        """
        self.assert_success_response(response, 200)
        data = response.json()
        
        # Check wrapper structure
        assert "confidence" in data, "Missing confidence field"
        assert "data" in data, "Missing data field"
        assert "predictionTime" in data, "Missing predictionTime field"
        
        # Check data structure
        invoice_data = data["data"]
        required_fields = [
            "InvoiceId", "VendorName", "InvoiceDate", "BillingAddressRecipient",
            "ShippingAddress", "SubTotal", "ShippingCost", "InvoiceTotal",
            "Tax", "Currency", "Items"
        ]
        
        for field in required_fields:
            assert field in invoice_data, f"Missing required field: {field}"
    
    def assert_po_schema(self, response):
        """
        Assert that PO response matches expected schema.
        
        Args:
            response: Response from PO upload endpoint.
        
        Raises:
            AssertionError: If schema doesn't match.
        """
        self.assert_success_response(response, 200)
        data = response.json()
        
        required_fields = [
            "po_number", "date", "supplier_name", "company_name",
            "delivery_date", "total_amount", "currency", "status", "items"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def assert_invalid_file_type_error(self, response):
        """
        Assert that response indicates invalid file type error.
        
        Args:
            response: Response object.
        
        Raises:
            AssertionError: If error is not as expected.
        """
        self.assert_error_response(response, 400)
        data = response.json()
        assert "detail" in data, "Missing error detail"
        assert "pdf" in data["detail"].lower(), "Error message should mention PDF"
