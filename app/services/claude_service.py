"""
Claude Service - Handles all interactions with Anthropic Claude API.

This service encapsulates:
- API client initialization
- PDF base64 encoding
- Claude message construction
- Response parsing and validation
"""

import base64
import logging
import re
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Service for interacting with Anthropic Claude API.
    
    Handles PDF encoding, API calls, and response validation.
    """
    
    def __init__(self, api_key_file: str = ".anthropickey"):
        """
        Initialize Claude service with API key.
        
        Args:
            api_key_file (str): Path to file containing Anthropic API key.
        
        Raises:
            FileNotFoundError: If API key file doesn't exist.
            ValueError: If API key is empty.
        """
        self.api_key = self._load_api_key(api_key_file)
        self.client = Anthropic(api_key=self.api_key)
        logger.info("Claude service initialized successfully")
    
    def _load_api_key(self, key_file: str) -> str:
        """
        Load API key from file.
        
        Args:
            key_file (str): Path to API key file.
        
        Returns:
            str: API key.
        
        Raises:
            FileNotFoundError: If key file doesn't exist.
            ValueError: If key is empty.
        """
        # Look for key file in project root (parent of app directory)
        if not os.path.isabs(key_file):
            # Get the project root directory (parent of app/)
            project_root = Path(__file__).parent.parent.parent
            key_path = project_root / key_file
        else:
            key_path = Path(key_file)
        
        if not key_path.exists():
            logger.error(f"API key file not found: {key_path}")
            raise FileNotFoundError(f"API key file not found: {key_file}")
        
        api_key = key_path.read_text().strip()
        if not api_key:
            logger.error("API key file is empty")
            raise ValueError("API key file is empty")
        
        logger.info(f"API key loaded from {key_path}")
        return api_key
    
    @staticmethod
    def encode_pdf_to_base64(file_path: str) -> str:
        """
        Encode PDF file to base64 string.
        
        Args:
            file_path (str): Path to PDF file.
        
        Returns:
            str: Base64-encoded PDF content.
        
        Raises:
            FileNotFoundError: If PDF file doesn't exist.
        """
        pdf_path = Path(file_path)
        if not pdf_path.exists():
            logger.error(f"PDF file not found: {file_path}")
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        with open(pdf_path, "rb") as pdf_file:
            encoded = base64.standard_b64encode(pdf_file.read()).decode('utf-8')
        
        logger.debug(f"Encoded PDF: {file_path} ({len(encoded)} chars)")
        return encoded
    
    def parse_document(
        self,
        pdf_path: str,
        prompt_text: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 1024
    ) -> str:
        """
        Parse document using Claude with PDF input.
        
        Args:
            pdf_path (str): Path to PDF file.
            prompt_text (str): Complete prompt with instructions.
            model (str): Claude model to use.
            max_tokens (int): Maximum response tokens.
        
        Returns:
            str: Raw response from Claude.
        
        Raises:
            Exception: If API call fails.
        """
        logger.info(f"Parsing document: {pdf_path}")
        
        # Encode PDF to base64
        pdf_base64 = self.encode_pdf_to_base64(pdf_path)
        
        try:
            # Create message with document input
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt_text
                            }
                        ]
                    }
                ]
            )
            
            # Extract text response
            response_text = message.content[0].text
            logger.info(f"Successfully parsed document with Claude")
            logger.debug(f"Response length: {len(response_text)} chars")
            
            return response_text
        
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise
    
    @staticmethod
    def clean_json_response(response: str) -> str:
        """
        Clean JSON response by removing code fences and extra text.
        
        Args:
            response (str): Raw response from Claude.
        
        Returns:
            str: Cleaned JSON string.
        """
        # Remove markdown code fences
        cleaned = re.sub(r'^```json\s*', '', response)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        
        # Extract JSON from code fences if present
        json_match = re.search(r'```json\s*(.*?)\s*```', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(1)
        
        logger.debug(f"Cleaned JSON response ({len(cleaned)} chars)")
        return cleaned.strip()
    
    @staticmethod
    def parse_json(json_string: str) -> Dict[str, Any]:
        """
        Parse JSON string to dictionary.
        
        Args:
            json_string (str): JSON string to parse.
        
        Returns:
            Dict[str, Any]: Parsed JSON as dictionary.
        
        Raises:
            json.JSONDecodeError: If JSON is invalid.
        """
        import json
        try:
            data = json.loads(json_string)
            logger.debug(f"Successfully parsed JSON with {len(data)} keys")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise
    
    def parse_and_validate(
        self,
        pdf_path: str,
        prompt_text: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Complete pipeline: parse document and return validated dictionary.
        
        Args:
            pdf_path (str): Path to PDF file.
            prompt_text (str): Complete prompt with instructions.
            model (str): Claude model.
            max_tokens (int): Max response tokens.
        
        Returns:
            Dict[str, Any]: Parsed and validated data.
        
        Raises:
            Exception: If parsing or validation fails.
        """
        # Get response from Claude
        raw_response = self.parse_document(
            pdf_path=pdf_path,
            prompt_text=prompt_text,
            model=model,
            max_tokens=max_tokens
        )
        
        # Clean and parse JSON
        cleaned_json = self.clean_json_response(raw_response)
        parsed_data = self.parse_json(cleaned_json)
        
        logger.info(f"Document parsing complete: {len(parsed_data)} fields extracted")
        return parsed_data
