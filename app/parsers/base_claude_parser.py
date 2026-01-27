"""
Base Claude Parser - Abstract interface for Claude-based document parsers.

All Claude parsers must inherit from this class and implement the abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseClaudeParser(ABC):
    """
    Abstract base class for Claude-based document parsers.
    
    This class defines the interface that all Claude parsers must implement.
    It enforces separation of concerns and provides a consistent API.
    """
    
    def __init__(self, file_path: str, claude_service):
        """
        Initialize the parser.
        
        Args:
            file_path (str): Path to the PDF document.
            claude_service: Instance of ClaudeService for API calls.
        """
        self.file_path = file_path
        self.claude_service = claude_service
        self.parsed_data = None
        logger.info(f"Initialized {self.__class__.__name__} for: {file_path}")
    
    @abstractmethod
    def get_prompt(self) -> str:
        """
        Get the prompt for this document type.
        
        Returns:
            str: Complete prompt with instructions.
        """
        pass
    
    @abstractmethod
    def validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the parsed data according to schema.
        
        Args:
            data (Dict[str, Any]): Raw parsed data from Claude.
        
        Returns:
            Dict[str, Any]: Validated and cleaned data.
        
        Raises:
            ValueError: If validation fails.
        """
        pass
    
    def validate_file_exists(self) -> bool:
        """
        Check if the PDF file exists.
        
        Returns:
            bool: True if file exists, False otherwise.
        """
        return Path(self.file_path).exists()
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the document using Claude API.
        
        This is the main entry point for document parsing.
        
        Returns:
            Dict[str, Any]: Parsed and validated document data.
        
        Raises:
            FileNotFoundError: If PDF file doesn't exist.
            ValueError: If parsing or validation fails.
        """
        if not self.validate_file_exists():
            logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        logger.info(f"Starting parsing with Claude: {self.file_path}")
        
        try:
            # Get prompt
            prompt_text = self.get_prompt()
            
            # Parse with Claude
            raw_data = self.claude_service.parse_and_validate(
                pdf_path=self.file_path,
                prompt_text=prompt_text
            )
            
            # Validate schema
            self.parsed_data = self.validate_schema(raw_data)
            
            logger.info(f"Successfully parsed {self.__class__.__name__}")
            return self.parsed_data
        
        except Exception as e:
            logger.error(f"Parsing failed: {str(e)}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the parsed data as a dictionary.
        
        Returns:
            Dict[str, Any]: Parsed document data.
        
        Raises:
            RuntimeError: If document hasn't been parsed yet.
        """
        if self.parsed_data is None:
            logger.error("Document not parsed yet. Call parse() first.")
            raise RuntimeError("Document not parsed yet. Call parse() first.")
        
        return self.parsed_data
