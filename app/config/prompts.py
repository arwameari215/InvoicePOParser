"""
Versioned and documented prompts for Claude document parsing.

All prompts are centralized here for easy maintenance and version control.
"""

from typing import Dict

# Prompt version
PROMPT_VERSION = "1.0.0"


class InvoicePrompts:
    """Prompts for invoice parsing."""
    
    PROMPT = """
Please extract the following invoice fields: InvoiceId, VendorName, InvoiceDate, BillingAddressRecipient, ShippingAddress, SubTotal, ShippingCost, InvoiceTotal, Tax, Items.

Notes:
- Output a JSON format ONLY, without any additional text.
- InvoiceId: The invoice number/ID from the document.
- VendorName: The vendor/supplier name.
- InvoiceDate: Must be in format YYYY-MM-DD (the year from the document, NOT 2026). Hebrew invoices dates are usually European format (DD/MM/YYYY).
- BillingAddressRecipient: Billing address recipient (can be null).
- ShippingAddress: Shipping address (can be null).
- SubTotal: Subtotal amount before shipping/tax (number only, no currency symbol).
- ShippingCost: Shipping cost (number only, no currency symbol).
- InvoiceTotal: Total invoice amount (number only, no currency symbol).
- Tax: Tax amount (can be null if not found, number only).
- Items: List/array of line items (can be empty array [] if no items found). Each item should have relevant fields like description, quantity, price.
- Do not add any other entries except what you were tasked to extract.
"""


class PurchaseOrderPrompts:
    """Prompts for purchase order parsing."""
    
    PROMPT = """
Please extract: po_number, date, supplier_name, company_name, delivery_date, total_amount, status, items (list of objects with description, quantity, unit_price, total).

Notes:
- Output a JSON format ONLY, without any additional text.
- The po_number should be clean format (e.g., "PO-000X").
- The supplier_name should be clean, without prefixes like "Name:" or "Supplier:".
- The company_name is the company/organization that issued the purchase order (buyer company).
- Dates must be in format YYYY-MM-DD.
- Prices without the currency sign, only numbers.
- items must ALWAYS be a list/array of objects.
- Each item object should have: description, quantity, unit_price, total.
- Do not add any other entries except what you were tasked to extract.
"""


def get_invoice_prompts() -> Dict[str, str]:
    """
    Get invoice parsing prompt.
    
    Returns:
        Dict[str, str]: Dictionary with 'prompt' and 'version'.
    """
    return {
        "prompt": InvoicePrompts.PROMPT,
        "version": PROMPT_VERSION
    }


def get_po_prompts() -> Dict[str, str]:
    """
    Get purchase order parsing prompt.
    
    Returns:
        Dict[str, str]: Dictionary with 'prompt' and 'version'.
    """
    return {
        "prompt": PurchaseOrderPrompts.PROMPT,
        "version": PROMPT_VERSION
    }
