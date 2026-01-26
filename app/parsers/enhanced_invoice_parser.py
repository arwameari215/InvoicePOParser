"""
Enhanced Invoice Parser with confidence scoring and OCI-like structure.
"""

from typing import Dict, List, Any
import pdfplumber
import logging
import re
import time
from datetime import datetime
from .base_parser import DocumentParser

logger = logging.getLogger(__name__)


class EnhancedInvoiceParser(DocumentParser):
    """
    Enhanced parser for Invoice documents with confidence scoring.
    
    Extracts invoice data with confidence scores similar to OCI Document AI.
    """

    def __init__(self, file_path: str) -> None:
        """Initialize the Enhanced InvoiceParser."""
        super().__init__(file_path)
        self.pages = []
        self.raw_text = ""
        self.start_time = None

    def load_file(self) -> None:
        """Load the invoice PDF file into memory."""
        if not self.validate_file_exists():
            logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        try:
            self.start_time = time.time()
            pdf = pdfplumber.open(self.file_path)
            if len(pdf.pages) == 0:
                logger.error("PDF file is empty")
                raise ValueError("PDF file is empty")
            
            self.pages = pdf.pages
            self.document_data = pdf
            
            # Extract all text for processing
            for page in self.pages:
                page_text = page.extract_text()
                if page_text:
                    self.raw_text += page_text + "\n"
            
            logger.info(f"Successfully loaded invoice PDF with {len(self.pages)} pages")
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            raise ValueError(f"Error loading PDF: {str(e)}")

    def parse_metadata(self) -> Dict[str, Any]:
        """Extract metadata with confidence scores."""
        metadata = {}
        
        # Invoice ID
        invoice_data = self._extract_field(
            r'(?:invoice|inv)[\s#:]*([A-Z0-9-]+)',
            'InvoiceId'
        )
        metadata.update(invoice_data)
        
        # Vendor Name (company issuing invoice)
        vendor_data = self._extract_vendor_name()
        metadata.update(vendor_data)
        
        # Invoice Date
        date_data = self._extract_date()
        metadata.update(date_data)
        
        # Bill To (Customer)
        bill_to_data = self._extract_bill_to()
        metadata.update(bill_to_data)
        
        # Shipping Address
        ship_to_data = self._extract_ship_to()
        metadata.update(ship_to_data)
        
        # Financial fields
        subtotal_data = self._extract_field(
            r'(?:subtotal)[\s:$]*\$?([0-9,]+\.?\d{2})',
            'SubTotal',
            is_amount=True
        )
        metadata.update(subtotal_data)
        
        shipping_data = self._extract_field(
            r'(?:shipping)[\s:$]*\$?([0-9,]+\.?\d{2})',
            'ShippingCost',
            is_amount=True
        )
        metadata.update(shipping_data)
        
        total_data = self._extract_field(
            r'(?:balance due|total|grand total|amount due)[\s:$]*\$?([0-9,]+\.?\d{2})',
            'InvoiceTotal',
            is_amount=True
        )
        metadata.update(total_data)
        
        tax_data = self._extract_field(
            r'(?:tax|vat)[\s:$]*\$?([0-9,]+\.?\d{2})',
            'Tax',
            is_amount=True
        )
        metadata.update(tax_data)
        
        return metadata

    def _extract_field(self, pattern: str, field_name: str, is_amount: bool = False) -> Dict[str, Any]:
        """Extract a field with confidence score."""
        result = {
            field_name: None,
            f"{field_name}_confidence": 0.0
        }
        
        match = re.search(pattern, self.raw_text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if is_amount:
                value = float(value.replace(',', ''))
            result[field_name] = value
            result[f"{field_name}_confidence"] = 0.95  # High confidence for regex match
        
        return result

    def _extract_vendor_name(self) -> Dict[str, Any]:
        """Extract vendor/supplier name (company issuing invoice)."""
        result = {
            "VendorName": None,
            "VendorName_confidence": 0.0
        }
        
        # First line often has pattern "VendorName INVOICE" or just "VendorName"
        lines = self.raw_text.split('\n')
        if lines:
            first_line = lines[0].strip()
            # Extract vendor name before 'INVOICE' keyword
            if 'INVOICE' in first_line.upper():
                vendor = first_line.split('INVOICE')[0].strip()
                if vendor:
                    result["VendorName"] = vendor
                    result["VendorName_confidence"] = 0.95
            else:
                # Check first few lines for standalone company name
                for line in lines[:3]:
                    cleaned = line.strip()
                    if not cleaned or len(cleaned) < 2:
                        continue
                    skip_keywords = ['#', 'bill to:', 'ship to:', 'date:', 'balance', 
                                   'ship mode:', 'due:', 'total:', 'subtotal', 'order id']
                    if any(kw in cleaned.lower() for kw in skip_keywords):
                        continue
                    result["VendorName"] = cleaned
                    result["VendorName_confidence"] = 0.90
                    break
        
        return result

    def _extract_date(self) -> Dict[str, Any]:
        """Extract invoice date in ISO format."""
        result = {
            "InvoiceDate": None,
            "InvoiceDate_confidence": 0.0
        }
        
        date_patterns = [
            (r'(?:date)[\s:]*([A-Za-z]{3}\s+\d{2}\s+\d{4})', '%b %d %Y'),  # Mar 06 2012
            (r'(?:date)[\s:]*(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),
            (r'(?:date)[\s:]*(\d{2}/\d{2}/\d{4})', '%m/%d/%Y'),
        ]
        
        for pattern, date_format in date_patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1).strip()
                    parsed_date = datetime.strptime(date_str, date_format)
                    result["InvoiceDate"] = parsed_date.strftime('%Y-%m-%d')
                    result["InvoiceDate_confidence"] = 0.95
                    break
                except:
                    continue
        
        return result

    def _extract_bill_to(self) -> Dict[str, Any]:
        """Extract billing customer information."""
        result = {
            "BillingAddressRecipient": None,
            "BillingAddressRecipient_confidence": 0.0
        }
        
        lines = self.raw_text.split('\n')
        for i, line in enumerate(lines):
            # Find the line with "Bill To:" and customer name is typically few lines below
            if 'Bill To:' in line:
                # Check next few lines for customer name
                for j in range(i+1, min(i+4, len(lines))):
                    candidate = lines[j].strip()
                    # Skip empty lines, "Ship Mode", and lines with numbers at start (addresses)
                    if candidate and 'Ship Mode' not in candidate and not re.match(r'^\d', candidate):
                        # Extract just the name (before any numbers/addresses)
                        name_match = re.match(r'^([A-Za-z\s]+?)(?:\s+\d|$)', candidate)
                        if name_match:
                            result["BillingAddressRecipient"] = name_match.group(1).strip()
                            result["BillingAddressRecipient_confidence"] = 0.92
                            break
                break
        
        return result

    def _extract_ship_to(self) -> Dict[str, Any]:
        """Extract shipping address."""
        result = {
            "ShippingAddress": None,
            "ShippingAddress_confidence": 0.0
        }
        
        lines = self.raw_text.split('\n')
        for i, line in enumerate(lines):
            if 'Ship To:' in line:
                # Collect address lines starting from a few lines after "Ship To:"
                address_parts = []
                for j in range(i+1, min(i+6, len(lines))):
                    candidate = lines[j].strip()
                    
                    # Skip Ship Mode line
                    if 'Ship Mode' in candidate:
                        continue
                    
                    # Look for street address - extract from first number onwards
                    if not address_parts and re.search(r'\d{3,5}', candidate):
                        # Extract from the number onwards (skip name before it)
                        match = re.search(r'(\d{3,5}[^$]+)', candidate)
                        if match:
                            address_parts.append(match.group(1).strip())
                    # Add continuation lines (city, state, country)
                    elif address_parts and candidate:
                        if 'Balance' not in candidate and 'Due' not in candidate and not re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', candidate):
                            address_parts.append(candidate)
                    
                    # Stop if we hit item table
                    if 'Item' in candidate and 'Quantity' in candidate:
                        break
                
                if address_parts:
                    result["ShippingAddress"] = ','.join(address_parts)
                    result["ShippingAddress_confidence"] = 0.90
                break
        
        return result

    def parse_items(self) -> List[Dict[str, Any]]:
        """Extract line items from text."""
        items = []
        
        try:
            lines = self.raw_text.split('\n')
            in_items_section = False
            item_description = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Detect item table header
                if 'Item' in line and 'Quantity' in line and 'Rate' in line:
                    in_items_section = True
                    continue
                
                # Stop at summary section
                if in_items_section and ('Subtotal:' in line or 'Notes:' in line):
                    break
                
                if in_items_section and line:
                    # Parse item line: "ItemName Quantity $Price $Amount"
                    # Example: "Xerox 1906 4 $141.76 $567.04" or "Panasonic Kx-TS550 3 $82.78 $248.35"
                    item_match = re.match(r'^([A-Za-z0-9\s-]+?)\s+(\d+)\s+\$([0-9,.]+)\s+\$([0-9,.]+)', line)
                    if item_match:
                        item_name = item_match.group(1).strip()
                        quantity = int(item_match.group(2))
                        unit_price = float(item_match.group(3).replace(',', ''))
                        total = float(item_match.group(4).replace(',', ''))
                        
                        item_description = item_name
                        
                        # Check next line for additional description (like "Paper, Office Supplies")
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            # If next line doesn't start with a digit or $, it's probably additional description
                            if next_line and not re.match(r'^[\d$]', next_line) and 'Subtotal' not in next_line:
                                item_description = f"{item_name} {next_line}"
                        
                        items.append({
                            "description": item_description,
                            "quantity": quantity,
                            "unit_price": unit_price,
                            "total": total
                        })
        
        except Exception as e:
            logger.error(f"Error parsing items: {str(e)}")
        
        return items

    def _find_column_index(self, header: List[str], keywords: List[str]) -> int:
        """Find column index by keywords."""
        for i, col in enumerate(header):
            for keyword in keywords:
                if keyword in col:
                    return i
        return None

    def _parse_number(self, value: Any, default: float = 0.0) -> float:
        """Parse numeric value."""
        if value is None:
            return default
        try:
            cleaned = re.sub(r'[,$€£¥]', '', str(value)).strip()
            return float(cleaned) if cleaned else default
        except:
            return default

    def to_dict(self) -> Dict[str, Any]:
        """Return OCI-like structured response with confidence."""
        if self.document_data is None:
            raise RuntimeError("Document not loaded. Call load_file() first.")
        
        # Get metadata and items
        metadata = self.parse_metadata()
        items = self.parse_items()
        
        # Separate data from confidence (but don't return confidence separately)
        data = {}
        confidences = []
        
        for key, value in metadata.items():
            if key.endswith('_confidence'):
                # Track for overall confidence calculation only
                confidences.append(value)
            else:
                data[key] = value
        
        # Add items to data (remove individual confidence scores)
        clean_items = []
        for item in items:
            clean_item = {}
            for k, v in item.items():
                if not k.endswith('_confidence'):
                    clean_item[k] = v
                elif v > 0:
                    confidences.append(v)
            clean_items.append(clean_item)
        
        data["Items"] = clean_items
        
        # Calculate overall document confidence
        doc_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        prediction_time = time.time() - self.start_time if self.start_time else 0.0
        
        return {
            "confidence": round(doc_confidence, 2),
            "data": data,
            "predictionTime": round(prediction_time, 3)
        }
