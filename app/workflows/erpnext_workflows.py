"""
ERPNext Workflows Module

Contains complete workflows for submitting Purchase Orders and Sales Invoices to ERPNext.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from app.services.erpnext_service import (
    ensure_entity_exists,
    create_entity,
    update_entity,
    get_entity,
    ValidationError,
    ERPNextAPIError
)


logger = logging.getLogger(__name__)


# ============================================================================
# Validation Functions
# ============================================================================

def validate_purchase_order_input(form_data: Dict[str, Any]) -> None:
    """
    Validate Purchase Order input before submission.
    
    Args:
        form_data: Purchase order data
    
    Raises:
        ValidationError: If validation fails
    """
    # Required fields
    if not form_data.get('company_name'):
        raise ValidationError('Company name is required')
    
    if not form_data.get('supplier_name'):
        raise ValidationError('Supplier name is required')
    
    if not form_data.get('date'):
        raise ValidationError('Order date is required')
    
    if not form_data.get('delivery_date'):
        raise ValidationError('Delivery date is required')
    
    # Items validation
    items = form_data.get('items', [])
    if not items or len(items) == 0:
        raise ValidationError('At least one item is required')
    
    # Validate each item
    for i, item in enumerate(items, 1):
        # Item code
        if not item.get('item_code'):
            raise ValidationError(f'Item {i}: item_code is required')
        
        # Quantity
        qty = float(item.get('qty') or item.get('quantity') or 0)
        if qty <= 0:
            raise ValidationError(f'Item {i}: quantity must be greater than 0')
        
        # Rate
        rate = float(item.get('rate') or item.get('unit_price') or 0)
        if rate < 0:
            raise ValidationError(f'Item {i}: rate cannot be negative')


def validate_sales_invoice_input(form_data: Dict[str, Any]) -> None:
    """
    Validate Sales Invoice input before submission.
    
    Args:
        form_data: Sales invoice data
    
    Raises:
        ValidationError: If validation fails
    """
    # Required fields
    if not form_data.get('company_name') or not form_data.get('company_name').strip():
        raise ValidationError('Please specify a company before creating the invoice')
    
    if not form_data.get('customer_name') or not form_data.get('customer_name').strip():
        raise ValidationError('Please select a customer before creating the invoice')
    
    if not form_data.get('posting_date'):
        raise ValidationError('Invoice date is required')
    
    if not form_data.get('due_date'):
        raise ValidationError('Due date is required')
    
    # Date validation
    try:
        posting_date = datetime.strptime(form_data['posting_date'], '%Y-%m-%d')
        due_date = datetime.strptime(form_data['due_date'], '%Y-%m-%d')
        
        if due_date < posting_date:
            raise ValidationError('Due date cannot be earlier than invoice date')
    except ValueError as e:
        if 'does not match format' in str(e):
            raise ValidationError('Invalid date format. Use YYYY-MM-DD')
        raise
    
    # Items validation
    items = form_data.get('items', [])
    if not items or len(items) == 0:
        raise ValidationError('An invoice must include at least one item')
    
    # Validate each item
    for i, item in enumerate(items, 1):
        # Item code
        if not item.get('item_code') and not item.get('category'):
            raise ValidationError(f'Item {i}: Item code is required')
        
        # Description
        if not item.get('description'):
            raise ValidationError(f'Item {i}: Description is required')
        
        # Quantity
        qty = float(item.get('quantity') or item.get('qty') or 0)
        if qty <= 0:
            raise ValidationError(f'Item {i}: Quantity must be greater than zero')
        
        # Rate
        rate = float(item.get('rate') or item.get('unit_price') or 0)
        if rate < 0:
            raise ValidationError(f'Item {i}: Rate cannot be negative')
    
    # Shipping cost validation
    shipping_cost = float(form_data.get('shipping_cost', 0))
    if shipping_cost < 0:
        raise ValidationError('Shipping cost cannot be negative')


# ============================================================================
# Entity Ensure Functions
# ============================================================================

def ensure_company(company_name: str, on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Check if Company exists, create if not.
    
    Args:
        company_name: Company name
        on_status: Status callback function
    
    Returns:
        Company data dict
    
    Raises:
        ERPNextAPIError: If operation fails
    """
    payload = {
        'company_name': company_name,
        'abbr': company_name[:3].upper(),
        'default_currency': 'USD',
        'country': 'United States'
    }
    
    return ensure_entity_exists('Company', company_name, payload, on_status)


def ensure_supplier(supplier_name: str, on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Check if Supplier exists, create if not.
    
    Args:
        supplier_name: Supplier name
        on_status: Status callback function
    
    Returns:
        Supplier data dict
    
    Raises:
        ERPNextAPIError: If operation fails
    """
    payload = {
        'supplier_name': supplier_name,
        'supplier_type': 'Company'
    }
    
    return ensure_entity_exists('Supplier', supplier_name, payload, on_status)


def ensure_customer(customer_name: str, on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Check if Customer exists, create if not.
    
    Args:
        customer_name: Customer name
        on_status: Status callback function
    
    Returns:
        Customer data dict
    
    Raises:
        ERPNextAPIError: If operation fails
    """
    payload = {
        'customer_name': customer_name,
        'customer_type': 'Individual',
        'customer_group': 'All Customer Groups',
        'territory': 'All Territories'
    }
    
    return ensure_entity_exists('Customer', customer_name, payload, on_status)


def ensure_item(item: Dict[str, Any], on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Check if Item exists, create if not.
    
    Args:
        item: Item data containing item_code and optional item_name
        on_status: Status callback function
    
    Returns:
        Item data dict
    
    Raises:
        ERPNextAPIError: If operation fails
    """
    item_code = item.get('item_code') or item.get('category')
    item_name = item.get('item_name') or item.get('description') or item_code
    
    payload = {
        'item_code': item_code,
        'item_name': item_name,
        'item_group': 'All Item Groups',
        'stock_uom': 'Nos',
        'is_stock_item': 0
    }
    
    return ensure_entity_exists('Item', item_code, payload, on_status)


def ensure_items(items: List[Dict[str, Any]], on_status: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """
    Check if Items exist, create each if not.
    
    Args:
        items: List of item data dicts
        on_status: Status callback function
    
    Returns:
        List of item data dicts
    
    Raises:
        ERPNextAPIError: If operation fails
    """
    results = []
    
    for item in items:
        result = ensure_item(item, on_status)
        results.append(result)
    
    return results


# ============================================================================
# Purchase Order Workflow
# ============================================================================

def create_purchase_order(po_data: Dict[str, Any], on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Create Purchase Order in draft status.
    
    Args:
        po_data: Purchase order data
        on_status: Status callback function
    
    Returns:
        Created PO data with 'name' field (PO number)
    
    Raises:
        ERPNextAPIError: If creation fails
    """
    if on_status:
        on_status("Creating Purchase Order...")
    
    # Get company abbreviation for warehouse
    company = get_entity('Company', po_data['company_name'])
    company_abbr = company['abbr']
    
    payload = {
        'supplier': po_data['supplier_name'],
        'company': po_data['company_name'],
        'currency': po_data.get('currency', 'USD'),
        'transaction_date': po_data['date'],
        'schedule_date': po_data['delivery_date'],
        'items': []
    }
    
    # Transform items
    for item in po_data['items']:
        payload['items'].append({
            'item_code': item.get('item_code'),
            'qty': float(item.get('qty') or item.get('quantity') or 1),
            'rate': float(item.get('rate') or item.get('unit_price') or 0),
            'warehouse': f"Stores - {company_abbr}"
        })
    
    # Create PO
    response = create_entity('Purchase Order', payload)
    
    po_number = response['name']
    
    if on_status:
        on_status(f"Purchase Order {po_number} created successfully ✓")
    
    return response


def submit_purchase_order(po_name: str, on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Submit Purchase Order (change docstatus to 1).
    
    Args:
        po_name: Purchase Order name/number
        on_status: Status callback function
    
    Returns:
        Submitted PO data
    
    Raises:
        ERPNextAPIError: If submission fails
    """
    if on_status:
        on_status(f"Submitting Purchase Order {po_name}...")
    
    payload = {'docstatus': 1}
    
    response = update_entity('Purchase Order', po_name, payload)
    
    if on_status:
        on_status(f"Purchase Order {po_name} submitted successfully ✓")
    
    return response


def submit_purchase_order_workflow(
    form_data: Dict[str, Any],
    on_status: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Complete Purchase Order workflow.
    
    Args:
        form_data: {
            'company_name': str,
            'supplier_name': str,
            'date': str (YYYY-MM-DD),
            'delivery_date': str (YYYY-MM-DD),
            'currency': str (optional, default 'USD'),
            'items': [
                {
                    'item_code': str,
                    'item_name': str (optional),
                    'qty' or 'quantity': float,
                    'rate' or 'unit_price': float
                }
            ]
        }
        on_status: Callback for status updates
    
    Returns:
        dict: {
            'success': True,
            'po_name': 'PO-00001',
            'po_data': {...}
        }
    
    Raises:
        ValidationError: If input validation fails
        ERPNextAPIError: If ERPNext API call fails
    """
    # Step 1: Validate
    validate_purchase_order_input(form_data)
    
    # Step 2: Ensure Company
    ensure_company(form_data['company_name'], on_status)
    
    # Step 3: Ensure Supplier
    ensure_supplier(form_data['supplier_name'], on_status)
    
    # Step 4: Ensure Items
    ensure_items(form_data['items'], on_status)
    
    # Step 5: Create PO
    created_po = create_purchase_order(form_data, on_status)
    
    # Step 6: Submit PO
    submitted_po = submit_purchase_order(created_po['name'], on_status)
    
    return {
        'success': True,
        'po_name': submitted_po['name'],
        'po_data': submitted_po
    }


# ============================================================================
# Sales Invoice Workflow
# ============================================================================

def create_sales_invoice(invoice_data: Dict[str, Any], on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Create Sales Invoice in draft status.
    
    Args:
        invoice_data: Sales invoice data
        on_status: Status callback function
    
    Returns:
        Created invoice data with 'name' field
    
    Raises:
        ERPNextAPIError: If creation fails
    """
    if on_status:
        on_status("Creating Sales Invoice...")
    
    payload = {
        'customer': invoice_data['customer_name'],
        'company': invoice_data['company_name'],
        'currency': invoice_data.get('currency', 'USD'),
        'posting_date': invoice_data['posting_date'],
        'due_date': invoice_data['due_date'],
        'ignore_pricing_rule': 1,
        'items': []
    }
    
    # Transform items
    for item in invoice_data['items']:
        payload['items'].append({
            'item_code': item.get('item_code') or item.get('category'),
            'qty': float(item.get('qty') or item.get('quantity') or 1),
            'rate': float(item.get('rate') or item.get('unit_price') or 0)
        })
    
    # Add shipping charges if present
    shipping_cost = float(invoice_data.get('shipping_cost', 0))
    if shipping_cost > 0:
        payload['shipping_charges'] = shipping_cost
    
    # Create invoice
    response = create_entity('Sales Invoice', payload)
    
    invoice_number = response['name']
    
    if on_status:
        on_status(f"Sales Invoice {invoice_number} created successfully ✓")
    
    return response


def submit_sales_invoice(invoice_name: str, on_status: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Submit Sales Invoice (change docstatus to 1).
    
    Args:
        invoice_name: Sales Invoice name/number
        on_status: Status callback function
    
    Returns:
        Submitted invoice data
    
    Raises:
        ERPNextAPIError: If submission fails
    """
    if on_status:
        on_status(f"Submitting Sales Invoice {invoice_name}...")
    
    payload = {'docstatus': 1}
    
    response = update_entity('Sales Invoice', invoice_name, payload)
    
    if on_status:
        on_status(f"Sales Invoice {invoice_name} submitted successfully ✓")
    
    return response


def submit_sales_invoice_workflow(
    form_data: Dict[str, Any],
    on_status: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Complete Sales Invoice workflow.
    
    Args:
        form_data: {
            'company_name': str,
            'customer_name': str,
            'posting_date': str (YYYY-MM-DD),
            'due_date': str (YYYY-MM-DD),
            'currency': str (optional, default 'USD'),
            'shipping_cost': float (optional),
            'items': [
                {
                    'item_code' or 'category': str,
                    'description': str,
                    'qty' or 'quantity': float,
                    'rate' or 'unit_price': float
                }
            ]
        }
        on_status: Callback for status updates
    
    Returns:
        dict: {
            'success': True,
            'invoice_name': 'SINV-00001',
            'invoice_data': {...}
        }
    
    Raises:
        ValidationError: If input validation fails
        ERPNextAPIError: If ERPNext API call fails
    """
    # Step 1: Validate
    validate_sales_invoice_input(form_data)
    
    # Step 2: Ensure Company
    ensure_company(form_data['company_name'], on_status)
    
    # Step 3: Ensure Customer
    ensure_customer(form_data['customer_name'], on_status)
    
    # Step 4: Ensure Items
    ensure_items(form_data['items'], on_status)
    
    # Step 5: Create Invoice
    created_invoice = create_sales_invoice(form_data, on_status)
    
    # Step 6: Submit Invoice
    submitted_invoice = submit_sales_invoice(created_invoice['name'], on_status)
    
    return {
        'success': True,
        'invoice_name': submitted_invoice['name'],
        'invoice_data': submitted_invoice
    }
