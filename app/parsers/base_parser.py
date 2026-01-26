"""
Base abstract class for document parsing.
All specific parsers (Invoice, PO) must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentParser(ABC):
    """
    Abstract base class for document parsers.
    
    This class defines the interface that all document parsers must implement.
    It provides a structure for loading, parsing, and extracting data from documents.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the DocumentParser with a file path.
        
        Args:
            file_path (str): Path to the document file to be parsed.
        """
        self.file_path = file_path
        self.document_data = None
        logger.info(f"Initialized parser for file: {file_path}")

    @abstractmethod
    def load_file(self) -> None:
        """
        Load the document file into memory.
        
        This method should open and read the file, storing the necessary
        data structures for parsing.
        
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is invalid or empty.
        """
        pass

    @abstractmethod
    def parse_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the document.
        
        Returns:
            Dict[str, Any]: Dictionary containing document metadata such as
                           document number, date, supplier name, etc.
        """
        pass

    @abstractmethod
    def parse_items(self) -> List[Dict[str, Any]]:
        """
        Extract line items from the document.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries, each representing
                                  an item with description, quantity, price, etc.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the parsed document into a structured dictionary.
        
        This method combines metadata and items into a single output format.
        
        Returns:
            Dict[str, Any]: Complete document data with 'metadata' and 'items' keys.
        
        Raises:
            RuntimeError: If the file has not been loaded yet.
        """
        if self.document_data is None:
            logger.error("Document not loaded. Call load_file() first.")
            raise RuntimeError("Document not loaded. Call load_file() first.")
        
        metadata = self.parse_metadata()
        items = self.parse_items()
        
        result = {
            "metadata": metadata,
            "items": items
        }
        
        logger.info(f"Successfully parsed document: {self.file_path}")
        return result

    def validate_file_exists(self) -> bool:
        """
        Check if the file exists at the given path.
        
        Returns:
            bool: True if file exists, False otherwise.
        """
        import os
        return os.path.exists(self.file_path)
