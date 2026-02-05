"""
ERPNext Service Module

Core ERPNext API client for interacting with ERPNext REST API.
Handles entity operations (GET, POST, PUT) and error parsing.
"""

import re
import urllib.parse
import logging
from typing import Optional, Dict, Any
import requests

from app.config.erpnext_config import erpnext_config


logger = logging.getLogger(__name__)


class ERPNextAPIError(Exception):
    """Base exception for ERPNext API errors."""
    pass


class ValidationError(ERPNextAPIError):
    """Validation error before API call."""
    pass


class ExchangeRateError(ERPNextAPIError):
    """Exchange rate not configured in ERPNext."""
    pass


class ConnectionError(ERPNextAPIError):
    """Cannot connect to ERPNext."""
    pass


def parse_error_message(response: requests.Response) -> str:
    """
    Extract error message from ERPNext response.
    
    Args:
        response: HTTP response from ERPNext
    
    Returns:
        str: Parsed error message
    """
    try:
        data = response.json()
    except:
        return f"HTTP {response.status_code}: {response.text}"
    
    # Try multiple error fields
    error_message = (
        data.get('exception') or
        data.get('message') or
        data.get('_server_messages') or
        'Unknown error'
    )
    
    # Strip HTML tags
    error_message = re.sub(r'<[^>]*>', '', str(error_message))
    
    # Check for specific error types
    if any(keyword in error_message.lower() for keyword in 
           ['exchange rate', 'currency exchange', 'conversion rate']):
        raise ExchangeRateError(
            'Exchange rate not configured in ERPNext. '
            'Please go to ERPNext → Setup → Currency Exchange '
            'and add the exchange rate for your selected currency.'
        )
    
    return error_message


def api_request(
    endpoint: str, 
    method: str = 'GET', 
    body: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Optional[Dict[str, Any]]:
    """
    Generic API request handler for ERPNext.
    
    Args:
        endpoint: API endpoint path (e.g., '/api/resource/Company')
        method: HTTP method (GET, POST, PUT, DELETE)
        body: Request body for POST/PUT requests
        timeout: Request timeout in seconds
    
    Returns:
        Response data dict or None (for 404)
    
    Raises:
        ERPNextAPIError: For API errors
        ConnectionError: For connection failures
        ValueError: If credentials are not configured
    """
    base_url = erpnext_config.get_base_url()
    url = f"{base_url}{endpoint}"
    
    try:
        headers = erpnext_config.get_headers()
    except ValueError as e:
        raise ERPNextAPIError(str(e))
    
    logger.info(f"ERPNext API Request: {method} {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=body, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=body, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Handle 404 (entity not found) - not an error for existence checks
        if response.status_code == 404:
            logger.info(f"Entity not found (404): {url}")
            return None
        
        # Parse response
        try:
            data = response.json()
        except:
            if not response.ok:
                raise ERPNextAPIError(f"HTTP {response.status_code}: {response.text}")
            return None
        
        # Check for errors
        if not response.ok:
            error_message = parse_error_message(response)
            logger.error(f"ERPNext API Error: {error_message}")
            raise ERPNextAPIError(f"ERPNext API Error: {error_message}")
        
        logger.info(f"ERPNext API Request successful")
        return data
    
    except requests.exceptions.ConnectionError as e:
        error_msg = (
            f"Cannot connect to ERPNext at {base_url}. "
            "Please ensure:\n"
            "1. ERPNext is running\n"
            "2. CORS is configured in ERPNext\n"
            "3. The URL is correct"
        )
        logger.error(error_msg)
        raise ConnectionError(error_msg)
    
    except requests.exceptions.Timeout:
        error_msg = "Request to ERPNext timed out"
        logger.error(error_msg)
        raise ERPNextAPIError(error_msg)
    
    except (ERPNextAPIError, ConnectionError, ExchangeRateError):
        raise
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise ERPNextAPIError(error_msg)


def get_entity(doctype: str, name: str) -> Optional[Dict[str, Any]]:
    """
    Get an entity by name from ERPNext.
    
    Args:
        doctype: ERPNext doctype (e.g., 'Company', 'Supplier')
        name: Entity name/identifier
    
    Returns:
        Entity data dict or None if not found
    
    Raises:
        ERPNextAPIError: If API call fails
    """
    encoded_name = urllib.parse.quote(name)
    endpoint = f"/api/resource/{doctype}/{encoded_name}"
    
    response = api_request(endpoint, method='GET')
    
    if response is None:
        return None
    
    return response.get('data')


def create_entity(doctype: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new entity in ERPNext.
    
    Args:
        doctype: ERPNext doctype (e.g., 'Company', 'Supplier')
        payload: Entity data to create
    
    Returns:
        Created entity data dict
    
    Raises:
        ERPNextAPIError: If creation fails
    """
    endpoint = f"/api/resource/{doctype}"
    
    response = api_request(endpoint, method='POST', body=payload)
    
    if response is None:
        raise ERPNextAPIError(f"Failed to create {doctype}")
    
    return response.get('data')


def update_entity(doctype: str, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing entity in ERPNext.
    
    Args:
        doctype: ERPNext doctype (e.g., 'Purchase Order', 'Sales Invoice')
        name: Entity name/identifier
        payload: Fields to update
    
    Returns:
        Updated entity data dict
    
    Raises:
        ERPNextAPIError: If update fails
    """
    encoded_name = urllib.parse.quote(name)
    endpoint = f"/api/resource/{doctype}/{encoded_name}"
    
    response = api_request(endpoint, method='PUT', body=payload)
    
    if response is None:
        raise ERPNextAPIError(f"Failed to update {doctype} {name}")
    
    return response.get('data')


def check_erpnext_connection() -> Dict[str, Any]:
    """
    Test connection to ERPNext.
    
    Returns:
        dict: {'success': bool, 'message': str, 'user': str (optional)}
    """
    try:
        endpoint = "/api/method/frappe.auth.get_logged_user"
        response = api_request(endpoint, method='GET')
        
        if response:
            user = response.get('message', 'unknown')
            return {
                'success': True,
                'message': 'Connected to ERPNext successfully',
                'user': user
            }
        else:
            return {
                'success': False,
                'message': 'Connection failed: No response from ERPNext'
            }
    
    except ConnectionError as e:
        return {
            'success': False,
            'message': str(e)
        }
    
    except ERPNextAPIError as e:
        return {
            'success': False,
            'message': f'ERPNext error: {str(e)}'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }


def ensure_entity_exists(
    doctype: str,
    identifier: str,
    create_payload: Dict[str, Any],
    on_status: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Generic create-if-not-exists implementation.
    
    Args:
        doctype: ERPNext doctype name (e.g., 'Company')
        identifier: Unique identifier to check
        create_payload: Data to create if not exists
        on_status: Status callback function
    
    Returns:
        Entity data dict
    
    Raises:
        ERPNextAPIError: If API call fails
    """
    # Check if exists
    if on_status:
        on_status(f"Checking {doctype}: {identifier}...")
    
    existing = get_entity(doctype, identifier)
    
    if existing:
        if on_status:
            on_status(f"{doctype} \"{identifier}\" already exists ✓")
        return existing
    
    # Create new
    if on_status:
        on_status(f"Creating {doctype}: {identifier}...")
    
    created = create_entity(doctype, create_payload)
    
    if on_status:
        on_status(f"{doctype} \"{identifier}\" created successfully ✓")
    
    return created
