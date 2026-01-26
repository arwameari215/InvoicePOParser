"""
Parser Factory - Returns appropriate parser based on document type.
"""

from typing import Union
import logging
import sys
import os

# Add parsers directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'parsers'))

from parsers.base_parser import DocumentParser
from parsers.po_parser import PurchaseOrderParser
from parsers.enhanced_invoice_parser import EnhancedInvoiceParser

logger = logging.getLogger(__name__)


class ParserFactory:
    """
    Factory class for creating document parsers.
    
    This class implements the Factory design pattern to instantiate
    the appropriate parser based on the document type.
    """

    @staticmethod
    def get_parser(doc_type: str, file_path: str) -> DocumentParser:
        """
        Get the appropriate parser based on document type.
        
        Args:
            doc_type (str): Type of document. Supported values: 'invoice', 'po'.
            file_path (str): Path to the document file.
        
        Returns:
            DocumentParser: Instance of the appropriate parser class.
        
        Raises:
            ValueError: If the document type is not supported.
        """
        doc_type_lower = doc_type.lower().strip()
        
        if doc_type_lower in ["invoice", "invoice_enhanced", "enhanced_invoice", "invoice-enhanced"]:
            logger.info(f"Creating EnhancedInvoiceParser for file: {file_path}")
            return EnhancedInvoiceParser(file_path)
        
        elif doc_type_lower in ["po", "purchase_order", "purchaseorder"]:
            logger.info(f"Creating PurchaseOrderParser for file: {file_path}")
            return PurchaseOrderParser(file_path)
        
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
