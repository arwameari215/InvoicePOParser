"""
ERPNext Integration Router

Handles all ERPNext-related endpoints for creating and retrieving entities.
"""

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import logging

from app.workflows.erpnext_workflows import (
    submit_purchase_order_workflow,
    submit_sales_invoice_workflow
)
from app.services.erpnext_service import (
    check_erpnext_connection,
    get_entity,
    ValidationError,
    ERPNextAPIError,
    ExchangeRateError,
    ConnectionError as ERPNextConnectionError
)


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/erpnext", tags=["ERPNext Integration"])


# ============================================================================
# Connection Test
# ============================================================================

@router.get("/test-connection")
async def test_erpnext_connection() -> JSONResponse:
    """
    Test connection to ERPNext.
    
    Returns:
        JSONResponse: Connection test result
    """
    logger.info("Testing ERPNext connection")
    
    result = check_erpnext_connection()
    
    status_code = 200 if result['success'] else 500
    return JSONResponse(content=result, status_code=status_code)


# ============================================================================
# Read-Only Endpoints (for UI pre-population and validation)
# ============================================================================

@router.get("/company/{company_name}")
async def get_company_details(company_name: str) -> JSONResponse:
    """
    Get Company details from ERPNext (read-only).
    
    Useful for:
    - Pre-filling form data
    - Validating company exists before submission
    - Getting company currency/country info
    
    Path Parameters:
        company_name: Name of the company to retrieve
    
    Returns:
        JSONResponse: Company data or error
    """
    logger.info(f"Fetching company details: {company_name}")
    
    try:
        company_data = get_entity('Company', company_name)
        
        if company_data:
            return JSONResponse(content={
                'success': True,
                'data': company_data
            }, status_code=200)
        else:
            return JSONResponse(content={
                'success': False,
                'error': 'Company not found'
            }, status_code=404)
    
    except ERPNextAPIError as e:
        logger.error(f"Error fetching company: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)


@router.get("/supplier/{supplier_name}")
async def get_supplier_details(supplier_name: str) -> JSONResponse:
    """
    Get Supplier details from ERPNext (read-only).
    
    Useful for:
    - Pre-filling form data
    - Validating supplier exists before PO submission
    - Getting supplier type and group info
    
    Path Parameters:
        supplier_name: Name of the supplier to retrieve
    
    Returns:
        JSONResponse: Supplier data or error
    """
    logger.info(f"Fetching supplier details: {supplier_name}")
    
    try:
        supplier_data = get_entity('Supplier', supplier_name)
        
        if supplier_data:
            return JSONResponse(content={
                'success': True,
                'data': supplier_data
            }, status_code=200)
        else:
            return JSONResponse(content={
                'success': False,
                'error': 'Supplier not found'
            }, status_code=404)
    
    except ERPNextAPIError as e:
        logger.error(f"Error fetching supplier: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)


@router.get("/customer/{customer_name}")
async def get_customer_details(customer_name: str) -> JSONResponse:
    """
    Get Customer details from ERPNext (read-only).
    
    Useful for:
    - Pre-filling form data
    - Validating customer exists before invoice submission
    - Getting customer type, group, and territory info
    
    Path Parameters:
        customer_name: Name of the customer to retrieve
    
    Returns:
        JSONResponse: Customer data or error
    """
    logger.info(f"Fetching customer details: {customer_name}")
    
    try:
        customer_data = get_entity('Customer', customer_name)
        
        if customer_data:
            return JSONResponse(content={
                'success': True,
                'data': customer_data
            }, status_code=200)
        else:
            return JSONResponse(content={
                'success': False,
                'error': 'Customer not found'
            }, status_code=404)
    
    except ERPNextAPIError as e:
        logger.error(f"Error fetching customer: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)


@router.get("/item/{item_code}")
async def get_item_details(item_code: str) -> JSONResponse:
    """
    Get Item details from ERPNext (read-only).
    
    Useful for:
    - Pre-filling form data
    - Validating item exists before submission
    - Getting item name, UOM, and pricing info
    
    Path Parameters:
        item_code: Code/ID of the item to retrieve
    
    Returns:
        JSONResponse: Item data or error
    """
    logger.info(f"Fetching item details: {item_code}")
    
    try:
        item_data = get_entity('Item', item_code)
        
        if item_data:
            return JSONResponse(content={
                'success': True,
                'data': item_data
            }, status_code=200)
        else:
            return JSONResponse(content={
                'success': False,
                'error': 'Item not found'
            }, status_code=404)
    
    except ERPNextAPIError as e:
        logger.error(f"Error fetching item: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }, status_code=500)


# ============================================================================
# Write Endpoints (for submitting documents)
# ============================================================================

@router.post("/purchase-order")
async def submit_purchase_order_to_erpnext(data: Dict[str, Any] = Body(...)) -> JSONResponse:
    """
    Submit Purchase Order to ERPNext.
    
    Workflow:
    1. Validate input data
    2. Ensure Company exists (create if not)
    3. Ensure Supplier exists (create if not)
    4. Ensure Items exist (create each if not)
    5. Create Purchase Order in draft status
    6. Submit Purchase Order (docstatus=1)
    
    Request Body:
        {
            "company_name": str,
            "supplier_name": str,
            "date": str (YYYY-MM-DD),
            "delivery_date": str (YYYY-MM-DD),
            "currency": str (optional, default 'USD'),
            "items": [
                {
                    "item_code": str,
                    "item_name": str (optional),
                    "qty" or "quantity": float,
                    "rate" or "unit_price": float
                }
            ]
        }
    
    Returns:
        JSONResponse: {
            "success": true,
            "po_name": "PO-00001",
            "po_data": {...},
            "status_log": [...]
        }
    """
    logger.info("Received Purchase Order submission request")
    
    status_updates: List[str] = []
    
    def on_status(message: str):
        """Collect status updates"""
        status_updates.append(message)
        logger.info(f"[ERPNext] {message}")
    
    try:
        result = submit_purchase_order_workflow(data, on_status)
        
        return JSONResponse(content={
            'success': True,
            'po_name': result['po_name'],
            'po_data': result['po_data'],
            'status_log': status_updates
        }, status_code=201)
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'validation',
            'status_log': status_updates
        }, status_code=400)
    
    except ExchangeRateError as e:
        logger.error(f"Exchange rate error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'exchange_rate',
            'status_log': status_updates
        }, status_code=400)
    
    except ERPNextConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'connection',
            'status_log': status_updates
        }, status_code=503)
    
    except ERPNextAPIError as e:
        logger.error(f"ERPNext API error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'erpnext_api',
            'status_log': status_updates
        }, status_code=500)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(content={
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'error_type': 'unexpected',
            'status_log': status_updates
        }, status_code=500)


@router.post("/sales-invoice")
async def submit_sales_invoice_to_erpnext(data: Dict[str, Any] = Body(...)) -> JSONResponse:
    """
    Submit Sales Invoice to ERPNext.
    
    Workflow:
    1. Validate input data
    2. Ensure Company exists (create if not)
    3. Ensure Customer exists (create if not)
    4. Ensure Items exist (create each if not)
    5. Create Sales Invoice in draft status
    6. Submit Sales Invoice (docstatus=1)
    
    Request Body:
        {
            "company_name": str,
            "customer_name": str,
            "posting_date": str (YYYY-MM-DD),
            "due_date": str (YYYY-MM-DD),
            "currency": str (optional, default 'USD'),
            "shipping_cost": float (optional),
            "items": [
                {
                    "item_code" or "category": str,
                    "description": str,
                    "qty" or "quantity": float,
                    "rate" or "unit_price": float
                }
            ]
        }
    
    Returns:
        JSONResponse: {
            "success": true,
            "invoice_name": "SINV-00001",
            "invoice_data": {...},
            "status_log": [...]
        }
    """
    logger.info("Received Sales Invoice submission request")
    
    status_updates: List[str] = []
    
    def on_status(message: str):
        """Collect status updates"""
        status_updates.append(message)
        logger.info(f"[ERPNext] {message}")
    
    try:
        result = submit_sales_invoice_workflow(data, on_status)
        
        return JSONResponse(content={
            'success': True,
            'invoice_name': result['invoice_name'],
            'invoice_data': result['invoice_data'],
            'status_log': status_updates
        }, status_code=201)
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'validation',
            'status_log': status_updates
        }, status_code=400)
    
    except ExchangeRateError as e:
        logger.error(f"Exchange rate error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'exchange_rate',
            'status_log': status_updates
        }, status_code=400)
    
    except ERPNextConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'connection',
            'status_log': status_updates
        }, status_code=503)
    
    except ERPNextAPIError as e:
        logger.error(f"ERPNext API error: {str(e)}")
        return JSONResponse(content={
            'success': False,
            'error': str(e),
            'error_type': 'erpnext_api',
            'status_log': status_updates
        }, status_code=500)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(content={
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'error_type': 'unexpected',
            'status_log': status_updates
        }, status_code=500)
