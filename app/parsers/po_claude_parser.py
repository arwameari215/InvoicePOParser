"""
Purchase Order Claude Parser - Claude-based PO document parser.

Extracts purchase order data using Anthropic Claude with strict schema validation.
"""

from typing import Dict, Any, List
import logging
import re
from datetime import datetime
from .base_claude_parser import BaseClaudeParser
from config.prompts import get_po_prompts

logger = logging.getLogger(__name__)


class PurchaseOrderClaudeParser(BaseClaudeParser):
    """
    Parser for purchase orders using Claude AI.
    
    Extracts PO-specific fields with strict validation:
    - po_number
    - date (YYYY-MM-DD)
    - supplier_name
    - company_name (buyer company)
    - delivery_date (YYYY-MM-DD)
    - total_amount
    - status
    - items (list of item objects)
    """
    
    # Expected schema fields
    REQUIRED_FIELDS = [
        "po_number", "date", "supplier_name", "company_name", "delivery_date",
        "total_amount", "currency", "status", "items"
    ]
    
    # Expected item fields
    ITEM_FIELDS = ["description", "quantity", "unit_price", "total"]
    
    def get_prompt(self) -> str:
        """
        Get PO prompt.
        
        Returns:
            str: Complete prompt for PO parsing.
        """
        prompts = get_po_prompts()
        return prompts["prompt"]
    
    def validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate PO data against schema.
        
        Args:
            data (Dict[str, Any]): Raw data from Claude.
        
        Returns:
            Dict[str, Any]: Validated data.
        
        Raises:
            ValueError: If validation fails.
        """
        logger.info("Validating PO schema")
        
        # Check for extra keys
        extra_keys = set(data.keys()) - set(self.REQUIRED_FIELDS)
        if extra_keys:
            logger.warning(f"Removing extra keys: {extra_keys}")
            for key in extra_keys:
                del data[key]
        
        # Validate each field
        validated = {}
        
        # po_number - must be string
        validated["po_number"] = self._validate_po_number(data.get("po_number"))
        
        # dates - must be YYYY-MM-DD
        validated["date"] = self._validate_date(data.get("date"), "date")
        validated["delivery_date"] = self._validate_date(data.get("delivery_date"), "delivery_date")
        
        # supplier_name - must be clean string
        validated["supplier_name"] = self._validate_supplier_name(data.get("supplier_name"))
        
        # company_name - must be clean string
        validated["company_name"] = self._validate_company_name(data.get("company_name"))
        
        # total_amount - must be number
        validated["total_amount"] = self._validate_number(data.get("total_amount"), "total_amount")
        
        # currency - must be string
        validated["currency"] = self._validate_currency(data.get("currency"))
        
        # status - must be string
        validated["status"] = self._validate_status(data.get("status"))
        
        # items - must be list
        validated["items"] = self._validate_items(data.get("items"))
        
        logger.info("PO schema validation passed")
        return validated
    
    def _validate_po_number(self, value: Any) -> str:
        """Validate PO number field."""
        if value is None:
            return None
        
        po_num = str(value).strip()
        
        # Clean up any prefixes like "Number: PO-000X"
        po_num = re.sub(r'^(Number|PO Number|Purchase Order):\s*', '', po_num, flags=re.IGNORECASE)
        
        logger.debug(f"Validated PO number: {po_num}")
        return po_num
    
    def _validate_supplier_name(self, value: Any) -> str:
        """
        Validate supplier name - must be clean string without prefixes.
        """
        if value is None:
            return None
        
        name = str(value).strip()
        
        # Remove common prefixes
        name = re.sub(r'^(Supplier|Vendor|Name):\s*', '', name, flags=re.IGNORECASE)
        
        # Remove placeholder patterns like <...>
        if re.match(r'^<.*>$', name):
            name = re.sub(r'[<>]', '', name)
        
        logger.debug(f"Validated supplier name: {name}")
        return name
    
    def _validate_company_name(self, value: Any) -> str:
        """
        Validate company name - must be clean string without prefixes.
        """
        if value is None:
            return None
        
        name = str(value).strip()
        
        # Remove common prefixes
        name = re.sub(r'^(Company|Organization|Name):\s*', '', name, flags=re.IGNORECASE)
        
        # Remove placeholder patterns like <...>
        if re.match(r'^<.*>$', name):
            name = re.sub(r'[<>]', '', name)
        
        logger.debug(f"Validated company name: {name}")
        return name
    
    def _validate_date(self, value: Any, field_name: str) -> str:
        """
        Validate date field - must be YYYY-MM-DD.
        """
        if value is None:
            return None
        
        date_str = str(value).strip()
        
        # Try to parse date
        try:
            # Handle YYYY-MM-DD
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Handle DD/MM/YYYY
            elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                dt = datetime.strptime(date_str, "%d/%m/%Y")
            # Handle MM/DD/YYYY
            elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                dt = datetime.strptime(date_str, "%m/%d/%Y")
            else:
                logger.warning(f"Unknown date format for {field_name}: {date_str}")
                return None
            
            validated_date = dt.strftime("%Y-%m-%d")
            logger.debug(f"Validated {field_name}: {validated_date}")
            return validated_date
        
        except ValueError as e:
            logger.error(f"Date validation failed for {field_name}: {str(e)}")
            return None
    
    def _validate_number(self, value: Any, field_name: str) -> float:
        """
        Validate numeric field.
        """
        if value is None:
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
    
    def _validate_status(self, value: Any) -> str:
        """Validate status field."""
        if value is None:
            return "Pending"
        
        status = str(value).strip().capitalize()
        logger.debug(f"Validated status: {status}")
        return status
    
    def _validate_items(self, items: Any) -> List[Dict[str, Any]]:
        """
        Validate items list.
        
        Args:
            items: Items data (should be list).
        
        Returns:
            List[Dict[str, Any]]: Validated items list.
        """
        if items is None or not isinstance(items, list):
            logger.warning("Items is not a list, returning empty list")
            return []
        
        validated_items = []
        
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                logger.warning(f"Item {idx} is not a dictionary, skipping")
                continue
            
            validated_item = {}
            
            # description
            validated_item["description"] = str(item.get("description", "")).strip() or None
            
            # quantity
            validated_item["quantity"] = self._validate_number(
                item.get("quantity"), 
                f"item[{idx}].quantity"
            )
            
            # unit_price
            validated_item["unit_price"] = self._validate_number(
                item.get("unit_price"), 
                f"item[{idx}].unit_price"
            )
            
            # total
            validated_item["total"] = self._validate_number(
                item.get("total"), 
                f"item[{idx}].total"
            )
            
            # Only add if has description
            if validated_item["description"]:
                validated_items.append(validated_item)
        
        logger.debug(f"Validated {len(validated_items)} items")
        return validated_items
