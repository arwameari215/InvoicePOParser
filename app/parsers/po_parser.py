"""
Purchase Order Parser - Parses PO documents and extracts structured data.
"""

from typing import Dict, List, Any
import pdfplumber
import logging
import re
from .base_parser import DocumentParser

logger = logging.getLogger(__name__)


class PurchaseOrderParser(DocumentParser):
    """
    Parser for Purchase Order (PO) documents.
    
    Extracts PO-specific information such as PO number, date, supplier name,
    items, total amount, delivery date, and status.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the PurchaseOrderParser.
        
        Args:
            file_path (str): Path to the PO PDF file.
        """
        super().__init__(file_path)
        self.pages = []

    def load_file(self) -> None:
        """
        Load the PO PDF file into memory using pdfplumber.
        
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the PDF is empty or invalid.
        """
        if not self.validate_file_exists():
            logger.error(f"File not found: {self.file_path}")
            raise FileNotFoundError(f"File not found: {self.file_path}")
        
        try:
            pdf = pdfplumber.open(self.file_path)
            if len(pdf.pages) == 0:
                logger.error("PDF file is empty")
                raise ValueError("PDF file is empty")
            
            self.pages = pdf.pages
            self.document_data = pdf
            logger.info(f"Successfully loaded PO PDF with {len(self.pages)} pages")
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            raise ValueError(f"Error loading PDF: {str(e)}")

    def parse_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the PO document.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - po_number (str)
                - date (str)
                - supplier_name (str)
                - delivery_date (str)
                - total_amount (float)
                - status (str)
        """
        metadata = {
            "po_number": None,
            "date": None,
            "supplier_name": None,
            "delivery_date": None,
            "total_amount": 0.0,
            "status": "Pending"
        }

        try:
            # Extract text from first page
            if self.pages:
                text = self.pages[0].extract_text()
                
                # Extract PO number
                po_match = re.search(r'(?:po|purchase order|p\.o\.)[\s#:]*([A-Z0-9-]+)', text, re.IGNORECASE)
                if po_match:
                    metadata["po_number"] = po_match.group(1)
                
                # Extract date
                date_patterns = [
                    r'(?:date|po date|order date)[\s:]*(\d{4}-\d{2}-\d{2})',
                    r'(?:date|po date|order date)[\s:]*(\d{2}/\d{2}/\d{4})',
                    r'(?:date|po date|order date)[\s:]*(\d{2}-\d{2}-\d{4})'
                ]
                for pattern in date_patterns:
                    date_match = re.search(pattern, text, re.IGNORECASE)
                    if date_match:
                        metadata["date"] = date_match.group(1)
                        break
                
                # Extract supplier name
                supplier_match = re.search(r'(?:supplier|vendor|to)[\s:]*([^\n]+)', text, re.IGNORECASE)
                if supplier_match:
                    metadata["supplier_name"] = supplier_match.group(1).strip()
                else:
                    # Fallback: use first meaningful line
                    lines = text.split('\n')
                    for line in lines[:8]:
                        if line.strip() and not any(kw in line.lower() for kw in ['purchase', 'order', 'po', 'date']):
                            metadata["supplier_name"] = line.strip()
                            break
                
                # Extract delivery date
                delivery_patterns = [
                    r'(?:delivery date|ship date|expected delivery)[\s:]*(\d{4}-\d{2}-\d{2})',
                    r'(?:delivery date|ship date|expected delivery)[\s:]*(\d{2}/\d{2}/\d{4})',
                    r'(?:delivery date|ship date|expected delivery)[\s:]*(\d{2}-\d{2}-\d{4})'
                ]
                for pattern in delivery_patterns:
                    delivery_match = re.search(pattern, text, re.IGNORECASE)
                    if delivery_match:
                        metadata["delivery_date"] = delivery_match.group(1)
                        break
                
                # Extract total amount
                total_match = re.search(r'(?:total|grand total|po total)[\s:$]*([0-9,]+\.?\d*)', text, re.IGNORECASE)
                if total_match:
                    metadata["total_amount"] = float(total_match.group(1).replace(',', ''))
                
                # Extract status
                status_match = re.search(r'(?:status)[\s:]*([A-Za-z]+)', text, re.IGNORECASE)
                if status_match:
                    metadata["status"] = status_match.group(1).strip()
                
                logger.info(f"Extracted PO metadata: {metadata}")
        
        except Exception as e:
            logger.error(f"Error parsing PO metadata: {str(e)}")
        
        return metadata

    def parse_items(self) -> List[Dict[str, Any]]:
        """
        Extract line items from the PO document.
        
        Returns:
            List[Dict[str, Any]]: List of items, each containing:
                - description (str)
                - quantity (int)
                - unit_price (float)
                - total (float)
        """
        items = []

        try:
            for page in self.pages:
                # Extract tables from the page
                tables = page.extract_tables()
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Assume first row is header
                    header = [str(cell).lower() if cell else '' for cell in table[0]]
                    
                    # Find column indices
                    desc_idx = self._find_column_index(header, ['description', 'item', 'product', 'details', 'material'])
                    qty_idx = self._find_column_index(header, ['quantity', 'qty', 'units', 'ordered'])
                    price_idx = self._find_column_index(header, ['unit price', 'price', 'rate', 'unit_price', 'cost'])
                    total_idx = self._find_column_index(header, ['total', 'amount', 'line total', 'extended'])
                    
                    # Parse rows
                    for row in table[1:]:
                        if not row or len(row) == 0:
                            continue
                        
                        # Skip empty rows
                        if all(not cell or str(cell).strip() == '' for cell in row):
                            continue
                        
                        item = {}
                        
                        # Extract description
                        if desc_idx is not None and desc_idx < len(row):
                            item["description"] = str(row[desc_idx]).strip() if row[desc_idx] else "N/A"
                        
                        # Extract quantity
                        if qty_idx is not None and qty_idx < len(row):
                            item["quantity"] = self._parse_number(row[qty_idx], default=0)
                        
                        # Extract unit price
                        if price_idx is not None and price_idx < len(row):
                            item["unit_price"] = self._parse_number(row[price_idx], default=0.0)
                        
                        # Extract total
                        if total_idx is not None and total_idx < len(row):
                            item["total"] = self._parse_number(row[total_idx], default=0.0)
                        
                        # Only add item if it has a meaningful description
                        if "description" in item and item["description"] and item["description"] != "N/A":
                            items.append(item)
            
            logger.info(f"Extracted {len(items)} items from PO")
        
        except Exception as e:
            logger.error(f"Error parsing PO items: {str(e)}")
        
        return items

    def _find_column_index(self, header: List[str], keywords: List[str]) -> int:
        """
        Find the index of a column based on keywords.
        
        Args:
            header (List[str]): Header row of the table.
            keywords (List[str]): List of possible column names.
        
        Returns:
            int: Index of the column, or None if not found.
        """
        for i, col in enumerate(header):
            for keyword in keywords:
                if keyword in col:
                    return i
        return None

    def _parse_number(self, value: Any, default: float = 0.0) -> float:
        """
        Parse a numeric value from a string, handling various formats.
        
        Args:
            value (Any): Value to parse.
            default (float): Default value if parsing fails.
        
        Returns:
            float: Parsed numeric value.
        """
        if value is None:
            return default
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[,$€£¥]', '', str(value)).strip()
            return float(cleaned) if cleaned else default
        except (ValueError, AttributeError):
            return default
