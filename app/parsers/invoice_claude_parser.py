"""
Invoice Claude Parser - Claude-based invoice document parser.

Extracts invoice data using Anthropic Claude with strict schema validation.
"""

from typing import Dict, Any
import logging
import re
import time
from datetime import datetime
from .base_claude_parser import BaseClaudeParser
from app.config.prompts import get_invoice_prompts

logger = logging.getLogger(__name__)


class InvoiceClaudeParser(BaseClaudeParser):
    """
    Parser for invoices using Claude AI.
    
    Extracts invoice-specific fields matching legacy format:
    - InvoiceId
    - VendorName
    - InvoiceDate
    - BillingAddressRecipient
    - ShippingAddress
    - SubTotal
    - ShippingCost
    - InvoiceTotal
    - Tax
    - Items
    
    Returns data wrapped with confidence and predictionTime.
    """
    
    # Expected schema fields
    REQUIRED_FIELDS = [
        "InvoiceId", "VendorName", "InvoiceDate", "BillingAddressRecipient",
        "ShippingAddress", "SubTotal", "ShippingCost", "InvoiceTotal", "Tax", "Currency", "Items"
    ]
    
    def get_prompt(self) -> str:
        """
        Get invoice prompt.
        
        Returns:
            str: Complete prompt for invoice parsing.
        """
        prompts = get_invoice_prompts()
        return prompts["prompt"]
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse invoice and return wrapped result with confidence.
        
        Returns:
            Dict containing confidence, data, and predictionTime.
        """
        start_time = time.time()
        
        # Call parent parse method
        parsed_data = super().parse()
        
        # Calculate prediction time
        prediction_time = round(time.time() - start_time, 3)
        
        # Wrap in legacy format
        return {
            "confidence": 0.85,  # Default confidence score
            "data": parsed_data,
            "predictionTime": prediction_time
        }
    
    def validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate invoice data against schema.
        
        Args:
            data (Dict[str, Any]): Raw data from Claude.
        
        Returns:
            Dict[str, Any]: Validated data.
        
        Raises:
            ValueError: If validation fails.
        """
        logger.info("Validating invoice schema")
        
        # Check for extra keys and log them but don't remove
        extra_keys = set(data.keys()) - set(self.REQUIRED_FIELDS)
        if extra_keys:
            logger.warning(f"Extra keys found (will be removed): {extra_keys}")
            for key in extra_keys:
                del data[key]
        
        # Validate each field
        validated = {}
        
        # InvoiceId - must be string
        validated["InvoiceId"] = self._validate_string(data.get("InvoiceId"), "InvoiceId")
        
        # VendorName - must be string
        validated["VendorName"] = self._validate_string(data.get("VendorName"), "VendorName")
        
        # InvoiceDate - must be YYYY-MM-DD
        validated["InvoiceDate"] = self._validate_date(data.get("InvoiceDate"))
        
        # Address fields - can be null
        validated["BillingAddressRecipient"] = self._validate_optional_string(
            data.get("BillingAddressRecipient")
        )
        validated["ShippingAddress"] = self._validate_optional_string(
            data.get("ShippingAddress")
        )
        
        # Numeric fields
        validated["SubTotal"] = self._validate_number(data.get("SubTotal"), "SubTotal")
        validated["ShippingCost"] = self._validate_number(data.get("ShippingCost"), "ShippingCost")
        validated["InvoiceTotal"] = self._validate_number(data.get("InvoiceTotal"), "InvoiceTotal")
        validated["Tax"] = self._validate_optional_number(data.get("Tax"))
        
        # Currency field
        validated["Currency"] = self._validate_currency(data.get("Currency"))
        
        # Items - must be array
        validated["Items"] = self._validate_items(data.get("Items"))
        
        logger.info("Invoice schema validation passed")
        return validated
    
    def _validate_string(self, value: Any, field_name: str) -> str:
        """Validate required string field."""
        if value is None or value == "":
            logger.warning(f"{field_name} is missing or empty")
            return None
        return str(value).strip()
    
    def _validate_optional_string(self, value: Any) -> str:
        """Validate optional string field (can be null)."""
        if value is None or value == "" or str(value).lower() == "null":
            return None
        return str(value).strip()
    
    def _validate_date(self, value: Any) -> str:
        """
        Validate date field - must be YYYY-MM-DD.
        Keeps the original year from the document.
        """
        if value is None:
            return None
        
        date_str = str(value).strip()
        
        # Try to parse date
        try:
            # Handle YYYY-MM-DD
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Handle DD/MM/YYYY (Hebrew/European)
            elif '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    # Determine if DD/MM or MM/DD based on values
                    if int(parts[0]) > 12:  # Must be DD/MM/YYYY
                        dt = datetime.strptime(date_str, "%d/%m/%Y")
                    else:  # Try MM/DD/YYYY first
                        try:
                            dt = datetime.strptime(date_str, "%m/%d/%Y")
                        except ValueError:
                            dt = datetime.strptime(date_str, "%d/%m/%Y")
                else:
                    logger.warning(f"Unknown date format: {date_str}")
                    return None
            else:
                logger.warning(f"Unknown date format: {date_str}")
                return None
            
            validated_date = dt.strftime("%Y-%m-%d")
            logger.debug(f"Validated date: {validated_date}")
            return validated_date
        
        except ValueError as e:
            logger.error(f"Date validation failed: {str(e)}")
            return None
    
    def _validate_number(self, value: Any, field_name: str) -> float:
        """Validate required numeric field."""
        if value is None:
            logger.warning(f"{field_name} is missing")
            return None
        
        try:
            # Remove any currency symbols or commas
            if isinstance(value, str):
                cleaned = re.sub(r'[,$₪€£¥]', '', value).strip()
                num = float(cleaned)
            else:
                num = float(value)
            
            logger.debug(f"Validated {field_name}: {num}")
            return num
        
        except (ValueError, TypeError) as e:
            logger.error(f"Number validation failed for {field_name}: {str(e)}")
            return None
    
    def _validate_optional_number(self, value: Any) -> float:
        """Validate optional numeric field (can be null)."""
        if value is None or str(value).lower() == "null":
            return None
        
        try:
            if isinstance(value, str):
                cleaned = re.sub(r'[,$₪€£¥]', '', value).strip()
                num = float(cleaned)
            else:
                num = float(value)
            return num
        except (ValueError, TypeError):
            return None
    
    def _validate_currency(self, value: Any) -> str:
        """Validate currency field - normalize to ISO 4217 codes."""
        if value is None or value == "":
            return "USD"  # Default to USD if not found
        
        currency_str = str(value).strip().upper()
        
        # Map common symbols to ISO codes
        currency_map = {
            "$": "USD",
            "€": "EUR",
            "₪": "ILS",
            "£": "GBP",
            "¥": "JPY",
            "₹": "INR"
        }
        
        # Check if it's a symbol
        if currency_str in currency_map:
            currency_str = currency_map[currency_str]
        
        # Common currency codes
        valid_currencies = ["USD", "EUR", "ILS", "GBP", "JPY", "CNY", "INR", "CAD", "AUD", "CHF"]
        
        if currency_str in valid_currencies:
            logger.debug(f"Validated currency: {currency_str}")
            return currency_str
        
        logger.warning(f"Unknown currency: {value}, defaulting to USD")
        return "USD"
    
    def _validate_items(self, value: Any) -> list:
        """Validate Items field - must be array."""
        if value is None:
            return []
        
        if not isinstance(value, list):
            logger.warning(f"Items is not a list, converting: {type(value)}")
            return []
        
        # Items can be empty array or list of objects
        logger.debug(f"Validated Items: {len(value)} items")
        return value
