"""
Parser Factory - Returns appropriate Claude AI parser based on document type.

Uses Anthropic Claude for intelligent document parsing.
"""

import logging

from app.parsers.base_claude_parser import BaseClaudeParser
from app.parsers.invoice_claude_parser import InvoiceClaudeParser
from app.parsers.po_claude_parser import PurchaseOrderClaudeParser
from app.services.claude_service import ClaudeService

logger = logging.getLogger(__name__)


class ParserFactory:
    """
    Factory class for creating Claude AI document parsers.
    
    This class implements the Factory design pattern to instantiate
    the appropriate Claude AI parser based on the document type.
    """
    
    _claude_service = None
    
    @classmethod
    def _get_claude_service(cls) -> ClaudeService:
        """
        Get singleton Claude service instance.
        
        Returns:
            ClaudeService: Initialized Claude service.
        """
        if cls._claude_service is None:
            try:
                cls._claude_service = ClaudeService()
                logger.info("Claude service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude service: {str(e)}")
                raise
        return cls._claude_service

    @staticmethod
    def get_parser(
        doc_type: str, 
        file_path: str
    ) -> BaseClaudeParser:
        """
        Get the appropriate Claude AI parser based on document type.
        
        Args:
            doc_type (str): Type of document. Supported: 'invoice', 'po'.
            file_path (str): Path to the document file.
        
        Returns:
            BaseClaudeParser: Claude AI parser instance.
        
        Raises:
            ValueError: If the document type is not supported.
        """
        doc_type_lower = doc_type.lower().strip()
        
        # Get Claude service
        claude_service = ParserFactory._get_claude_service()
        
        # Invoice parser
        if doc_type_lower in ["invoice", "invoice_enhanced", "enhanced_invoice", "invoice-enhanced"]:
            logger.info(f"Creating InvoiceClaudeParser for file: {file_path}")
            return InvoiceClaudeParser(file_path, claude_service)
        
        # Purchase Order parser
        elif doc_type_lower in ["po", "purchase_order", "purchaseorder"]:
            logger.info(f"Creating PurchaseOrderClaudeParser for file: {file_path}")
            return PurchaseOrderClaudeParser(file_path, claude_service)
        
        else:
            error_msg = f"Unsupported document type: {doc_type}. Supported types: 'invoice', 'po'"
            logger.error(error_msg)
            raise ValueError(error_msg)

    @staticmethod
    def get_supported_types() -> list:
        """
        Get list of supported document types.
        
        Returns:
            list: List of supported document type strings.
        """
        return ["invoice", "po", "purchase_order"]
