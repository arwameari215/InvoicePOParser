"""
PDF Loader Utility - Helper class for loading and reading PDF files.
"""

import pdfplumber
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class PDFLoader:
    """
    Utility class for loading and extracting content from PDF files.
    
    This class provides helper methods to work with PDF documents,
    abstracting away the complexity of PDF manipulation libraries.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the PDFLoader with a file path.
        
        Args:
            file_path (str): Path to the PDF file.
        """
        self.file_path = file_path
        self.pdf = None

    def load(self) -> bool:
        """
        Load the PDF file.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.pdf = pdfplumber.open(self.file_path)
            logger.info(f"Successfully loaded PDF: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load PDF: {str(e)}")
            return False

    def get_pages(self) -> List:
        """
        Get all pages from the PDF.
        
        Returns:
            List: List of page objects.
        """
        if self.pdf is None:
            logger.warning("PDF not loaded. Call load() first.")
            return []
        return self.pdf.pages

    def get_page_count(self) -> int:
        """
        Get the number of pages in the PDF.
        
        Returns:
            int: Number of pages.
        """
        if self.pdf is None:
            return 0
        return len(self.pdf.pages)

    def extract_text(self, page_number: Optional[int] = None) -> str:
        """
        Extract text from a specific page or all pages.
        
        Args:
            page_number (Optional[int]): Page number (0-indexed). If None, extract from all pages.
        
        Returns:
            str: Extracted text.
        """
        if self.pdf is None:
            logger.warning("PDF not loaded. Call load() first.")
            return ""

        try:
            if page_number is not None:
                if 0 <= page_number < len(self.pdf.pages):
                    return self.pdf.pages[page_number].extract_text() or ""
                else:
                    logger.warning(f"Invalid page number: {page_number}")
                    return ""
            else:
                # Extract from all pages
                text = ""
                for page in self.pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""

    def extract_tables(self, page_number: int = 0) -> List:
        """
        Extract tables from a specific page.
        
        Args:
            page_number (int): Page number (0-indexed).
        
        Returns:
            List: List of tables (each table is a list of rows).
        """
        if self.pdf is None:
            logger.warning("PDF not loaded. Call load() first.")
            return []

        try:
            if 0 <= page_number < len(self.pdf.pages):
                tables = self.pdf.pages[page_number].extract_tables()
                return tables if tables else []
            else:
                logger.warning(f"Invalid page number: {page_number}")
                return []
        except Exception as e:
            logger.error(f"Error extracting tables: {str(e)}")
            return []

    def close(self) -> None:
        """
        Close the PDF file.
        """
        if self.pdf:
            self.pdf.close()
            logger.info("PDF file closed")

    def __enter__(self):
        """Context manager entry."""
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
